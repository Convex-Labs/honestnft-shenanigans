import { Connection, clusterApiUrl, PublicKey } from '@solana/web3.js';
import base58 from 'bs58';
import * as fs from 'fs';
import * as BufferLayout from '@solana/buffer-layout';
import axios from 'axios';
import { program } from "commander";
import { createObjectCsvWriter as createCsvWriter } from 'csv-writer';

const ATTRIBUTES_FOLDER = 'raw_attributes';

const AccountLayout = BufferLayout.struct([
  BufferLayout.u8('key'),
  BufferLayout.blob(32, 'update_authority'),
  BufferLayout.blob(32, 'mint'),
  BufferLayout.blob(32, 'name'),
  BufferLayout.blob(10, 'symbol'),
  BufferLayout.blob(4, "padding"),
  BufferLayout.blob(200, 'uri')
]);

const METAPLEX_PUBKEY = 'metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s';

async function getCollectionAccounts(authoirty) {
  let connection = new Connection(clusterApiUrl('mainnet-beta'));
  let metaplexPubkey = new PublicKey(METAPLEX_PUBKEY)
  const updateAuthorityFilter = {
    commitment: 'confirmed',
    filters: [
      {
        memcmp: {
          bytes: new PublicKey(authoirty).toBase58(),
          offset: 1
        }
      }
    ]
  }
  let programAccounts = await connection.getProgramAccounts(metaplexPubkey, updateAuthorityFilter);
  return programAccounts;
}

function getMetadataFromAccount(account) {
  const metadata = AccountLayout.decode(account.account.data, 0);
  const updateAuthority = base58.encode(metadata.update_authority)
  const mint = base58.encode(metadata.mint)
  const name = Buffer.from(metadata.name).toString().trim().replace(/[^ -~]+/g, ""); // magic regex to remove 
  const uri = Buffer.from(metadata.uri).toString().trim().replace(/[^ -~]+/g, "");   // non-ascii characters
  const id = parseInt(name.substring(name.indexOf('#') + 1))
  return {
    id: id,
    updateAuthority: updateAuthority,
    mint: mint,
    name: name,
    uri: uri,
    address: account.pubkey.toString()
  }
}

async function fetchMetadata(item, baseFolder) {
  const tokenFile = `${baseFolder}${item.id}.json`;
  let tokenMeta = null
  if (fs.existsSync(tokenFile)) {
    tokenMeta = JSON.parse(fs.readFileSync(tokenFile, 'utf-8'));
  } else {
    const { data } = await axios.get(item.uri);
    fs.writeFileSync(tokenFile, JSON.stringify(data, null, 2))
    tokenMeta = data;
  }

  console.log(item.name)
  const traits = {}

  traits['TOKEN_NAME'] = item.name;
  traits['TOKEN_ID'] = item.id;
  traits['TOKEN_ADDRESS'] = item.address;

  const attributes = tokenMeta.attributes || tokenMeta.traits;

  if (!attributes) {
    throw new Error('Failed to find the attribute key in the token ' + item.id);
  }

  attributes.forEach(attribute => {
    traits[attribute['trait_type']] = attribute['value'] ? attribute['value'] : 'None';
  })

  return traits;
}


async function fetchMetadataWithRetry(item, collectionDir, maxRetry = 5) {
  let trait = null
  for (let index = 0; index < maxRetry; index++) {
    try {
      trait = await fetchMetadata(item, collectionDir);
      break;
    } catch (e) {
      console.log('fetchMetadata error', e.toString());
    }
  }
  return trait
}

async function main(opts) {
  console.log(opts);

  const collectionName = opts.Collection;
  const collectionAuthority = opts.Contract;

  const collectionDir = `${ATTRIBUTES_FOLDER}/${collectionName}/`
  if (!fs.existsSync(ATTRIBUTES_FOLDER)) {
    fs.mkdirSync(ATTRIBUTES_FOLDER)
  }

  if (!fs.existsSync(collectionDir)) {
    fs.mkdirSync(collectionDir)
  }

  let cacheFile = `${collectionDir}${collectionAuthority}.json`;
  let collectionTokens = []
  if (fs.existsSync(cacheFile)) {
    collectionTokens = JSON.parse(fs.readFileSync(cacheFile, 'utf-8'));
  }

  if (!fs.existsSync(cacheFile)) {
    console.log('Query Tokens');
    let accountInfo = await getCollectionAccounts(collectionAuthority);
    for (const account of accountInfo) {
      let metadata = getMetadataFromAccount(account);
      collectionTokens.push(metadata)
    }
    fs.writeFileSync(cacheFile, JSON.stringify(collectionTokens, null, 2));
  }

  console.log('found', collectionTokens.length, 'tokens')
  console.log('sample', collectionTokens[0]);

  const batcthLimit = opts.Batch ? parseInt(opts.Batch) : 5;
  let pendingTasks = [];
  const maxRetry = 5;
  let allTraits = [];

  async function flush() {
    const batchResults = await Promise.all(pendingTasks);
    batchResults.forEach(result => {
      if (result) {
        allTraits.push(result);
      }
    })
    pendingTasks = [];
    console.log({
      total: collectionTokens.length,
      finished: allTraits.length,
      batcthLimit
    })
  }

  for (let index = 0; index < collectionTokens.length; index++) {
    const item = collectionTokens[index];
    pendingTasks.push(fetchMetadataWithRetry(item, collectionDir, maxRetry));
    if (pendingTasks.length > batcthLimit) {
      await flush();
    }
  }

  if (pendingTasks.length) await flush();

  const firstTrait = allTraits[0];
  const traitDBFile = `${ATTRIBUTES_FOLDER}/${collectionName}.csv`
  const header = Object.keys(firstTrait).map(_ => {
    return {
      id: _,
      title: _
    }
  }).filter(_ => _.id != 'TOKEN_ID');
  header.unshift({
    id: 'TOKEN_ID',
    title: 'TOKEN_ID'
  })
  const csvWriter = createCsvWriter({
    path: traitDBFile,
    header: header
  });
  console.log('allTraits', allTraits.length)
  await csvWriter.writeRecords(allTraits)
}

program
  .requiredOption('-contract <authority>', 'Collection contract id')
  .requiredOption('-collection <name>', 'Collection name')
  .option('-batch <number>', 'Batch limit')
  .description("CLI for pulling NFT metadata.")
  .action(async (opts, command) => {
    try {
      await main(opts);
    } catch (e) {
      console.log('error', e)
    }
  });

program.parse(process.argv);