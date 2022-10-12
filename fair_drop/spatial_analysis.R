require(tidyverse)
require(patchwork)
require(sp)
require(spatialEco)
options(scipen = 999)

collection_name <- "quaks"

# load rarity data
rarity_data <- read.csv(paste0("/data/rarity_data/", collection_name, "_raritytools.csv")) %>% 
  select(TOKEN_ID, Rank) 

# filter top ranked tokens for Spatial Analysis
# Assumption:
#           - if the overall distribution is random then the top ranked distribution is also random
max_rank <- 251
top250 <- rarity_data %>% filter(Rank < max_rank)

# create object of SpatialPoints-class 
top250.sp <- sp::SpatialPoints(cbind(top250$TOKEN_ID, top250$Rank))

# Actual top ranked tokens distribution statistics
spatialEco::nni(top250.sp)

# initialize list to store random distributions results
monty <- c()

for (i in 1:1000) {
  # Add columns with random distribution
  # rand_token - random distribution of token ids
  # rand_rank - random distribution of rarity rank
  temp_rand_token <- rarity_data %>% 
    mutate(rand_token = sample(TOKEN_ID, nrow(rarity_data), replace = FALSE),
           rand_rank = sample(Rank, nrow(rarity_data), replace = FALSE)) %>% 
    filter(rand_rank < max_rank)
  
  # create object of SpatialPoints-class 
  top250_rand.sp <- sp::SpatialPoints(cbind(temp_rand_token$TOKEN_ID, temp_rand_token$rand_rank))
  
  # append nni statistics for this random distribution
  monty <- append(monty, list(spatialEco::nni(top250_rand.sp)))
}

# collect all results into list for easier plotting
nni <- unlist(lapply(monty, function(x) x$NNI))
z.score <- unlist(lapply(monty, function(x) x$z.score))


# Opted to divide into squares with a side of (# tokens in collection)/25
# This gives as 25 * 25 total boxes
# TODO:
# Test sensitivity of results to this parameter
boxes <- seq(rarity_data$TOKEN_ID %>% min(),
             rarity_data$TOKEN_ID %>% max(),
             floor(nrow(rarity_data)/25))

# dataframe with random distribution of token id and token rank
rarity_data_rand <- rarity_data %>% 
  mutate(rand_token = sample(TOKEN_ID, nrow(rarity_data), replace = FALSE),
         rand_rank = sample(Rank, nrow(rarity_data), replace = FALSE))

# dummy lists to store results
temp <- c() # box counting result of actual collection distribution
temp_rand <- c() # box counting result of a random distribution

# TODO:
# Only doing box counting histogram for 1 random distribution
# Possible improvement would be to do a box counting for 1000 random distributions
# and show a density histogram
for (i in 1:(length(boxes)-1)) {
  for (j in 1:(length(boxes)-1)) {
    temp <- append(temp, rarity_data_rand %>% 
                     filter(TOKEN_ID < boxes[i+1] & TOKEN_ID >= boxes[i] & Rank < boxes[j+1] & Rank >= boxes[j]) %>%
                     nrow())
    temp_rand <- append(temp_rand, rarity_data_rand %>% 
                          filter(rand_token < boxes[i+1] & rand_token >= boxes[i] & rand_rank < boxes[j+1] & rand_rank >= boxes[j]) %>%
                          nrow())
  }
}

##############################
# Top ranked tokens rarity map
p1 <- ggplot(data = rarity_data %>% filter(Rank < 251), aes(x = TOKEN_ID, y = Rank)) +
  geom_point() + 
  labs(title = collection_name, subtitle = paste0("Rarity distribution for top ", max_rank - 1, " tokens"))

##############################
# NNI plot of 1000 random distributions
p2 <- ggplot(data = data.frame("simulation" = 1:length(nni), "nni" = nni),
             aes(x = simulation, y = nni)) + 
  geom_point() + 
  geom_hline(yintercept = spatialEco::nni(top250.sp)$NNI, linetype="dashed", 
             color = "red", size=1.5)  +
  labs(title = collection_name,
       subtitle = "NNI distribution for 1000 random distributions",
       caption = paste0("NNI for ", collection_name, " top ", max_rank - 1, " rarity tokens: ", round(spatialEco::nni(top250.sp)$NNI,2), "\n",
                        "Average NNI for 1000 random distributions: ", round(mean(nni),2)))

##############################
# NNI histogram of 1000 random distributions
p3 <- ggplot(data = data.frame("nni" = nni), aes(x = nni)) + 
  geom_histogram(bins = 25, color="black", fill="grey") + 
  geom_vline(xintercept=spatialEco::nni(top250.sp)$NNI, linetype="dashed", 
             color = "red", size=1.5) +
  labs(title = collection_name,
       subtitle = "NNI histogram for 1000 random distributions",
       caption = paste0("NNI index for ", collection_name, " top ", max_rank - 1, " rarity tokens: ", round(spatialEco::nni(top250.sp)$NNI,2)))

##############################
# z score plot of 1000 random distributions
p4 <- ggplot(data = data.frame("simulation" = 1:length(z.score), "z.score" = z.score),
             aes(x = simulation, y = z.score)) + 
  geom_point() + 
  geom_hline(yintercept = spatialEco::nni(top250.sp)$z.score, linetype="dashed", 
             color = "red", size=1.5)  +
  labs(title = collection_name,
       subtitle = "z score distribution for 1000 random distributions",
       caption = paste0("z-Score for ", collection_name, " top ", max_rank - 1, " rarity tokens: ", round(spatialEco::nni(top250.sp)$z.score,2), "\n",
                        "Average Z-Score for 1000 random distributions: ", round(mean(z.score),2)))


###############################
# # z score histogram of 1000 random distributions
# p4 <- ggplot(data = data.frame("z.score" = z.score), aes(x = z.score)) + 
#   geom_histogram(bins = 25, color="black", fill="grey") + 
#   geom_vline(xintercept=spatialEco::nni(top250.sp)$z.score, linetype="dashed", 
#              color = "red", size=1.5) +
#   labs(title = collection_name,
#        subtitle = "z score histogram for 1000 random distributions",
#        caption = paste0("z Score for ", collection_name, " top ", max_rank - 1, " rarity tokens: ", round(spatialEco::nni(top250.sp)$z.score,2)))

##############################
# box counting histogram of actual collection distribution
p5 <- ggplot(data = data.frame("boxCounting" = temp), aes(x = boxCounting)) + 
  geom_histogram(bins = 10, color="black", fill="grey") + 
  labs(title = collection_name,
       subtitle = "Box counting histogram",
       caption = paste0("Box size: ", floor(nrow(rarity_data)/25),
                        "\n Expected tokens in each box: ", round(floor(nrow(rarity_data)/25)^2/nrow(rarity_data),2),
                        "\n Box counting average: ", round(mean(temp),2),
                        "\n Box counting variance: ", round(var(temp),2))) +
  xlab("# of tokens in each box")

##############################
# box counting histogram of a random distribution
p6 <- ggplot(data = data.frame("boxCounting" = temp_rand), aes(x = boxCounting)) + 
  geom_histogram(bins = 10, color="black", fill="grey") + 
  labs(title = collection_name,
       subtitle = "Box counting histogram for a random distribution",
       caption = paste0("Box size: ", floor(nrow(rarity_data)/25),
                        "\n Expected tokens in each box: ", round(floor(nrow(rarity_data)/25)^2/nrow(rarity_data),2),
                        "\n Box counting average: ", round(mean(temp_rand),2),
                        "\n Box counting variance: ", round(var(temp_rand),2))) +
  xlab("# of tokens in box")

p1 + p2 + p3 + p4 + p5 + p6 + plot_layout(ncol = 2)