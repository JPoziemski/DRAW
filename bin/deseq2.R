library("DESeq2")

args = commandArgs(trailingOnly=TRUE)
count_matrix = args[1]
run_id = args[2]

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
write.csv(res, paste('../output/', run_id, '/VISUALISATION/res.csv', sep=""))
write.csv(assay(vsd), paste('../output/', run_id, '/VISUALISATION/vsd.csv', sep=""))
write.csv(assay(rld),paste('../output/', run_id, '/VISUALISATION/rld.csv', sep=""))
write.csv(normal, paste('../output/', run_id, '/VISUALISATION/norm.csv', sep=""))
write.csv(coldata, paste('../output/', run_id, '/VISUALISATION/anno.csv', sep=""))
