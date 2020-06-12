library("DESeq2")

args = commandArgs(trailingOnly=TRUE)
count_matrix = args[1]
run_id = args[2]



calculate_dds <- function(countData, colData){
    tryCatch(
        expr = {
            return(DESeqDataSetFromMatrix(countData = cts,
                              colData = coldata,
                              design = ~ treatment))
        },
        error = function(e){
            message('\nDesign has a single variable. Most likely the control data is missing. Was this intended?')
            return(DESeqDataSetFromMatrix(
                countData = countData,
                colData = colData,
                design = ~ 1))            
        },
        finally = {
            message('All done, quitting.')
        }
    )    
}


calculate_de <- function(dds){
    tryCatch(
        expr = {
            return(res <- results(dds, contrast=c('treatment', 'treated', 'control')))
        },
        error = function(e){
            message('\nDesign has a single variable. Most likely the control data is missing. Was this intended?')
            return(results(dds))    
        },
        finally = {
            message('All done, quitting.')
        }
    )    
}




# Read counts data and annotation
cts <- as.matrix(read.csv(count_matrix ,sep=",",row.names="gene_id"))
coldata <- data.frame("treatment" = colnames(cts))
rownames(coldata) <- colnames(cts)
coldata$treatment = sub(
    '(\\d)', '',
    coldata$treatment,
    perl=TRUE)


# Differential analysis
dds <- calculate_dds(cts, coldata)
dds <- DESeq(dds)
res <- calculate_de(dds)
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
