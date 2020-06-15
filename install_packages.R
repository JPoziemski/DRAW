if (!requireNamespace("BiocManager", quietly = TRUE))
    install.packages("BiocManager", repos = "http://cran.us.r-project.org")

BiocManager::install("RCurl")
BiocManager::install("DESeq2")