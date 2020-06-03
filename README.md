# ADP_project

ADP project: tool for RNA-seq analysis



##  Differential expression analysis
   
##  Visualisation 

The visualisation dashboard offers four type of plots, which can be accesed by selection appriopriate tab: 

**Smear plot**
  
Shows the the average log2 count per million (CPM, x-axis) versus log2 fold-change (FC, y-axis) of the change in gene expression. 

Text box allows choosing FDR cut-off. Red points indicate genes found to be significantly upregulated or downregulated by the treatment. All genes are labelled and their details can be accessed by moving the cursor over a gene of interest. 

**Volcano plot**
  
Volcano plot is a scatterplot showing statistical significance (p-value) versus magnitude of change (FC, fold-change). It enables quick visual identification of genes with large fold changes that are also statistically significant.

Thanks to text input it is possible to select p-value cut-off according to which the non-significant genes are separated from the sigificant ones, by colouring them in grey. The colour of significant genes in controlled by LogFC parameter. Text input allows for choosing the threshold by which the user decides which genes are considered up- (coloured in red) or down-regulated (coloroued in blue). All genes are labelled and their details can be accessed by moving the cursor over a gene of interest. 

**Heatmap**
  
Heatmap is prepared using *pairwise_distances* from *sklearn* library and *dendrogram* and linkage* from *scipy*.
The dendrogram at the side shows us a hierarchical clustering of the samples. 

FDR cut-off enables narrowing the genesclustered to a selection of choice. Additionally, the user can further subselect the genes, choosing the number of genes to plot with a given FDR.  All genes are labelled and their details can be accessed by moving the cursor over a gene of interest. 

**PCA**

Principal component analysis is performed and two principal compontents can be selected by user for plotting. 
