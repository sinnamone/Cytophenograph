from version import __version__
import optparse
from PhenoFunctions_v5 import *

parser = optparse.OptionParser(usage='python ./Cytophenograph/cytophenograph.v5.py -i $abs_path/Cytophenograph/Test_dataset/CD8_Panel_II_channelvalues_GA_downSampled/ -o $abs_path/Cytophenograph/output_test -k 300 -m $abs_path/Cytophenograph/Test_dataset/CD8_bulk_markers_to_exclude.txt -n Test -t 10 -p $abs_path/Cytophenograph/Test_dataset/Info_file_bulk_Test.xlsx -c VIA', version='2.0')
parser.add_option('-i', action="store", dest="input_folder", help='Absolute path of folder with CSV files.')
parser.add_option('-o', action="store", dest="output_folder", help='Absolute path of output folder. TIPS: Please use an empty folder.')
parser.add_option('-k', action="store", dest="kmeancoef", help='Number for nearest neighbors search for Phenograph execution.Deafult value is 30',
                  type='string', default='30')
parser.add_option('-m', action="store", dest="markerlist", help='Text file with features(channel name) to exclude during clustering execution.')
parser.add_option('-n', action="store", dest="analysis_name", help='Analysis name.')
parser.add_option('-t', action="store", dest="thread",type=int,default=1, help='Number of jobs.')
parser.add_option('-p', action="store", dest="pheno", help='Excel file with the following columns "Sample-Cell_type-EXP-ID-Time_point-Condition-Count", that will be integrated as metadata.')
parser.add_option('-c', type='choice', choices=['Phenograph', 'VIA', 'Flowsom'],
                  dest="clustering",
                  default="Phenograph", help='Tool selecting for clustering, Selection available are [Phenograph,VIA,Flowsom].')
parser.add_option('-b', action="store_true", dest="batch", default=False,
                  help='Perform batch correction with Scanorama.')
parser.add_option('-e', type='choice', choices=['Sample', 'Cell_type','ID', 'EXP', 'Time_point', 'Condition'],
                  dest="batchcov",
                  default="Sample", help='Please, specify covariate to correct with Scanorama')
parser.add_option('-d', action="store", dest="mindist", default=0.5,type=float, help='min_dist parameter for UMAP generation')
parser.add_option('-s', action="store", dest="spread", default=1,type=int, help='spread parameter for UMAP generation')
parser.add_option('-r', type='choice', choices=['full', 'umap', 'clustering'],
                  dest="runtime",
                  default="full", help='Runtime option for custom analysis. The available options are full , umap , clustering ')

parser.add_option('-w', action="store", dest="knn", help='Number of K-Nearest Neighbors for VIA KNN graph.Min allowed value is 5,Max allowed value is 100. Deafult value is 30',
                  type=int, default=30)
parser.add_option('-z', action="store", dest="resolution", help='A parameter value controlling the coarseness of the VIA clustering.Min allowed value is 0.2,Max allowed value is 1.5. Deafult value is 1.0',
                  type=float, default=1.0)
parser.add_option('-x', action="store", dest="minclus", help='Flowsom Min proposed number of clusters.Min allowed value is 5,Max allowed value is maxclus-2. Deafult value is 5',
                  type=int, default=5)
parser.add_option('-y', action="store", dest="maxclus", help='Flowsom Max proposed number of clusters.Min allowed value is minclus-2,Max allowed value is 31. Deafult value is 31',
                  type=int, default=31)

options, args = parser.parse_args()


if __name__ == '__main__':
    print("Script name: cytophenograph" )
    print("Script version:", __version__)
    print("Start")
    DictInfo = dict()

    run = Cytophenograph(info_file=options.pheno,
                         input_folder=options.input_folder,
                         output_folder=options.output_folder,
                         k_coef=options.kmeancoef,
                         marker_list=options.markerlist,
                         analysis_name=options.analysis_name,
                         thread=int(options.thread),
                         tool=options.clustering,
                         batch=options.batch,
                         batchcov=options.batchcov,
                         mindist=options.mindist,
                         spread=options.spread,
                         runtime=options.runtime,
                         knn=options.knn,
                         resolution=options.resolution,
                         minclus=options.minclus,
                         maxclus=options.maxclus)
    DictInfo["Infofile"] = run.read_info_file()
    DictInfo["List_csv_files"] = run.import_all_event()
    DictInfo["adata_conc"] = run.concatenate_dataframe(DictInfo["Infofile"],
                                                       DictInfo["List_csv_files"])
    DictInfo["pathmarkerfile"], DictInfo["basenamemarkerfilepath"] = run.loadmarkers()
    DictInfo["markertoexclude"] = run.checkmarkers()
    DictInfo["markertoinclude"] = run.splitmarker()
    if options.runtime != 'umap':
        if options.clustering == "Phenograph":
            print("Clustering tool selected is: Phenograph")
            DictInfo["phenograph_adata"] = run.runphenograph()
        elif options.clustering == "VIA":
            print("Clustering tool selected is: VIA")
            DictInfo["via_adata"] = run.runvia()
        elif options.clustering == "Flowsom":
            print("Clustering tool selected is: Flowsom")
            DictInfo["flowsom_adata"] = run.runflowsom()
        run.groupbycluster()
        run.groupbysample()
        run.exporting()
    if options.runtime == 'umap':
        print("UMAP generaration skipping clustering")
        run.runtimeumap()
        run.groupbysample()
        run.exporting()
    print("End")
