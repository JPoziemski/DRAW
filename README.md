# ADP_project

ADP project: tool for RNA-seq analysis


## Isolated environment in Docker containers

**Before starting the analysis make sure you have installed Docker (recommended version 19.03.8) and a popular web browser (recommended Google Chrome version 81.0.4044.113) on your Linux machine. It is the only installation needed, the rest does Docker itself.**

To install Docker on Linux folow instructions from website linked below:
```
https://runnable.com/docker/install-docker-on-linux
```

To get the image of DRAW, make sure you have Internet access and execute the following script:
```console
$ ./build.sh
```

**Before running the container place input data in the input directory.** To run the container execute the run_docker.sh script as below. Directories input, config_files and output persist data generated and used by Docker. Ports 2000 i 5000 are published to the host machine. Container is running in interactive mode for user to see running processes. It will open a GUI application to fill in configurations and visualizations server, which will rise after the end of the analysis.
```console
$ ./run_docker.sh
```

GUI and visualizations are available while Docker container is running, you can simply acces them typing URLs in your favourite browser as below. GUI is accessed by port 2000, visualizations by port 5000. Mind visualizations are available after generating config file and running analysis, which takes some time.

```
http://0.0.0.0:2000/index

http://0.0.0.0:5000/bkapp
```

To stop the docker from running use Ctrl+C

If encounter an error "Adress is already in use" type following command and port, which you want to release:
```console
$ sudo fuser -k Port_Number/tcp
```

Docker uses following options: \
--tag, -t Tag docker container. \
--publish , -p	Publish a container’s port(s) to the host \
--volume , -v	Bind a volume \
--interactive, -it Run container in interactive mode


##  Differential expression analysis

The differential expression analysis is performed in DESeq2. 
The output of the differential expression analysis are 4 files:
- Normalized counts
- rLog - regularized logarithm
- VST - variance stabilizing transformations
- DESeq2 result file


##  Visualisation 

The visualisation dashboard offers four type of plots, which can be accesed by selection appriopriate tab. Most often the visualisation dashboard will be opened as soon as the analysis is finished. 

When needed, the visualisation for a given run can be accessed in a seperate manner. All of the requirements for running the analysis apart from the Docker and the rest od the DRAW module, can be installed:

```console
$ ./vis_requirements.sh
```

Then, to run the visualisation:
```console
$  python bin/vis.py -id [run_id] -dt [data]
```

where ```run_id``` is the id of the run we want to visualise, and ```data``` is one of the followind data types:
- ```norm``` - normalized counts
- ```rlog``` - regularized logarithm
- ```vst``` - variance stabilizing transformation

The plots offered:

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
