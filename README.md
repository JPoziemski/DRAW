# ADP_project

ADP project: tool for RNA-seq analysis


## Isolated environment in Docker containers

**Before starting the analysis make sure you have installed Docker (recommended version 19.03.8) and a popular web browser (recommended Google Chrome:81.0.4044.113) on your Linux machine. It is the only installation needed, the rest does Docker itself.**

To get the image of DRAW, make sure you have Internet access and execute the following script:
```console
$ ./build.sh
```

Before running the container place input data in the input directory. To run the container execute the run_docker.sh script as below. Directories input, config_files and output persist data generated and used by Docker. Ports 2000 i 5000 are published to the host machine. Container is running in interactive mode to see running processes.
```console
$ ./run_docker.sh
```

To stop the docker from running use Ctrl + d


Docker uses following options: \
--tag, -t Tag docker container. \
--publish , -p	Publish a container’s port(s) to the host \
--volume , -v	Bind a volume \
--interactive, -it Run container in interactive mode


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
