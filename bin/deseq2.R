library("DESeq2")


args = commandArgs(trailingOnly=TRUE)
count_matrix = args[1]

# Read counts data and annotation
cts <- as.matrix(read.csv(count_matrix ,sep=",",row.names="gene_id"))
coldata <- data.frame("treatment" = colnames(cts))
rownames(coldata) <- colnames(cts)
coldata$treatment = sub(
    '(\\d)', '',
    coldata$treatment,
    perl=TRUE)


dds <- DESeqDataSetFromMatrix(countData = cts,
                              colData = coldata,
                              design = ~ treatment)

# Differential analysis
dds <- DESeq(dds)
res <- results(dds, contrast=c('treatment', 'treated', 'control'))
# Transform data
# Normalize
normal  <- counts(dds, normalized = TRUE)
# Variance stabilizing transformation
vsd <- varianceStabilizingTransformation(dds, blind = FALSE)
# Regularized-logarithm transformation
rld <- rlog(dds, blind = FALSE)

# Save outputs
write.csv(res, '../output/VISUALISATION/res.csv')
write.csv(assay(vsd),'../output/VISUALISATION/vsd.csv')
write.csv(assay(rld),'../output/VISUALISATION/rld.csv')
write.csv(normal,'../output/VISUALISATION/normal.csv')
write.csv(coldata,'../output/VISUALISATION/anno.csv')
