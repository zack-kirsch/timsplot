# =============================================================================
# Changelog
# =============================================================================
#region

#changes made from 240913 version
#region
    #metadata
        #changed how metadata works. Added 2nd table that only shows conditions so it makes reordering and concentration input much easier
        #it should update with removal of entire conditions' replicates in the replicate-based metadata table so long as the switch is active
        #changed how R.Condition, R.Replicate, and concentration are updated from the metadata, substantially faster by not going row-by-row 
    #throughout 
        #changed .str.contains(condition) to ==condition. There was a bug where - in the condition name would make the code interpret as an invalid decimal and mess up how it interpreted the conditions
        #adjusted titlefont, axisfont, labelfont, and legendfont throughout such that changing the sliders in the control panel adjusts the right groupings
    #idmetrics
        #added a sort for resultdf so that the conditions are ordered when it's generated. There was a bug where the ordering for the conditions would be correct based on the metadata (as in the x axis labels) in the idmetrics plot but the actual data were in order of condition because of the way the loop works
    #Settings
        #Control Panel 
            #tab added for font size control and other plotting customization
            #new variables to add throughout in plotting functions
            # titlefont=input.titlefont()
            # axisfont=input.axisfont()
            # labelfont=input.labelfont()
            # legendfont=input.legendfont()
            # ypadding=input.ypadding()
        #Column Check 
            #tab added to make sure necessary columns are present
        #Color Settings
            #changed the matplotlib and css color groups to images that were explicitly saved to \images under the Spectronaut_Vis_App folder
            #this makes them load faster and stay present even when the tab is reloaded
            #the functions are still present to render them as plots under
        #File Stats
            #added panel with useful information about the input file
    #Metrics
        #added separate functions for explicitly calculating metrics instead of using the idmetrics function. Should help in error handling
        #Peptide Lengths
            #adjusted x axis such that it always uses integer ticks for the x axis
        #Peptides per Protein  
            #adjusted plotting such that there is a hard cutoff to the high x range
            #adjusted plotting such that values were sorted properly, preventing odd plotting artefacts
        #Data Completeness
            #adjusted y padding and spacing for data labels
        #Added Peak Width section
    #PTMs
        #PTMs per Precursor
            #adjusted ylim top and x axis tick position
    #Heatmaps
        #RT, m/z, IM Heatmaps
            #adjusted single replicate choice to == instead of .str.contains
        #Charge/PTM Precursor Heatmap 
            #adjusted syntax in uploading custom dia windows
        #IDs vs RT
            #adjusted rtmax to just the nearest whole number instead of the nearest ten
        #Venn Diagram of IDs    
            #adjusted single replicate choice to == instead of .str.contains
        #Charge/PTM Scatter
            #added as a plotting option, shows precursors of picked charge or ptm against all the other precursors to show how charges/ptms group in the heatmap
    #Mixed Proteome
        #Counts per Organism
            #Added options for plotting peptides and precursors per organism instead of just proteins
    #Raw Data
        #Added EIM section
    #Added Dilution Series section
    #Added PCA section
    
#endregion
#changes made from 241021 version
#region
    #File Import
        #added the capability to download the metadata table as-shown as well as upload your own metadata table
        #added error handling for different software search reports. If columns are missing, it will ignore them in the .drop function
    #PTMs
        #adjusted ptmcounts function, no need for MS2Quantity columns and made it more comparable to the idmetrics function
    #Glycoproteomics
        #added section, working on adding different visualization functions
    #reordered some side tabs

#endregion

#endregion

# =============================================================================
# Library Imports
# =============================================================================
#region
from shiny import App, Inputs, Outputs, Session, reactive, render, ui, module
from shinyswatch import theme
#https://rstudio.github.io/shinythemes/
from shiny.types import ImgData
import alphatims.bruker as atb
import alphatims.plotting as atp
from collections import OrderedDict
from datetime import date
from faicons import icon_svg
#https://fontawesome.com/search?o=r&m=free
import io
import itertools
from itertools import groupby
import math
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
import matplotlib.colors as mcolors
from matplotlib.patches import Rectangle
from matplotlib.ticker import MaxNLocator
from matplotlib_venn import venn2,venn2_circles,venn3,venn3_circles
import numpy as np
import os
import pandas as pd
import pathlib
import re
from scipy.stats import norm
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from tkinter import *
from upsetplot import *

matplotlib.use('Agg')
#endregion

# =============================================================================
# UI
# =============================================================================
#region

app_ui=ui.page_fluid(
    ui.panel_title("timsTOF Proteomics Data Visualization"),
    ui.navset_pill_list(
        ui.nav_panel("File Import",
                     ui.card(
                         ui.card_header("Upload Search Report"),
                         ui.input_selectize("software","Search software:",{"spectronaut":"Spectronaut","diann":"DIA-NN","fragpipe":"FragPipe","timsdiann":"tims-DIANN (ProteoScape)","ddalibrary":"Spectronaut Library","fragpipe_glyco":"FragPipe (Glyco)"}),
                         ui.output_text("metadata_reminder"),
                         ui.input_file("searchreport","Upload search report:",accept=".tsv",multiple=False),
                         height="350px"
                         ),
                     ui.card(
                         ui.card_header("Update from Metadata Table"),
                         ui.row(
                             ui.column(4,
                                          ui.input_switch("condition_names","Update 'R.Condition' and 'R.Replicate' columns",width="100%"),
                                          ui.input_switch("remove","Remove selected runs")            
                                          ),
                             ui.column(4,
                                          ui.input_switch("reorder","Reorder runs"),
                                          ui.input_switch("concentration","Update 'Concentration' column")
                                )
                         ),
                        #  ui.input_switch("condition_names","Update 'R.Condition' and 'R.Replicate' columns",width="100%"),
                        #  ui.input_switch("remove","Remove selected runs"),
                        #  ui.input_switch("reorder","Reorder runs"),
                        #  ui.input_switch("concentration","Update 'Concentration' column"),
                         ui.input_action_button("rerun_metadata","Apply changes to search report / reinitialize search report",width="300px",class_="btn-primary",icon=icon_svg("rotate"))
                         ),
                     ui.card(
                         ui.card_header("Metadata Tables"),
                         ui.row(
                             ui.column(4,
                                       ui.input_file("metadata_upload","(Optional) Upload filled metadata table:",accept=".csv",multiple=False),
                                       ui.input_switch("use_uploaded_metadata","Use uploaded metadata table"),
                                       ),
                             ui.column(4,
                                       ui.download_button("metadata_download","Download metadata table as shown",width="300px",icon=icon_svg("file-arrow-down"))
                                       ),
                             ui.column(4,
                                       ui.p("Notes:"),
                                       ui.p("-To remove runs, add an 'x' to the 'remove' column"),
                                       ui.p("-To reorder conditions, order them numerically in the 'order' column")
                                       ),
                            ),
                         #ui.output_data_frame("metadata_table")
                         ui.row(
                             ui.column(8,
                             ui.output_data_frame("metadata_table")),
                             ui.column(4,
                             ui.output_data_frame("metadata_condition_table")))
                     ),icon=icon_svg("folder-open")
                    ),
        ui.nav_panel("Settings",
                     ui.navset_pill(
                         ui.nav_panel("Color Settings",
                                      ui.row(ui.column(4,
                                                       ui.input_radio_buttons("coloroptions","Choose coloring option for output plots:",choices={"pickrainbow":"Pick for me (rainbow)","pickmatplot":"Pick for me (matplotlib tableau)","custom":"Custom"},selected="pickmatplot"),
                                                       ui.input_text_area("customcolors","Input color names from the tables to the right, one per line:",autoresize=True),
                                                       ui.output_text("colornote"),
                                                       ui.row(ui.column(4,
                                                                        ui.output_table("customcolors_table1")
                                                                        ),
                                                              ui.column(4,
                                                                        ui.output_table("conditioncolors"),
                                                                        ui.output_plot("customcolors_plot")
                                                                        )
                                                              )
                                                       ),
                                             ui.column(2,
                                                       ui.output_text("matplotlibcolors_text"),
                                                       ui.output_image("matplotcolors_image")
                                                       #ui.output_plot("matplotlibcolors")
                                                       ),
                                             ui.column(5,
                                                       ui.output_text("csscolors_text"),
                                                       ui.output_image("csscolors_image")
                                                       #ui.output_plot("csscolors")
                                                       ),
                                             ),
                                     ui.output_ui("colorplot_height")
                                     ),
                         ui.nav_panel("File Stats",
                                      ui.output_table("filestats")
                                      ),
                         ui.nav_panel("Control Panel",
                                      ui.card(
                                          ui.card_header("Font Sizes"),
                                          ui.row(
                                              ui.input_slider("titlefont","Plot title size",min=10,max=25,value=20,step=1,ticks=True),
                                          ),
                                          ui.row(
                                              ui.input_slider("axisfont","Axis label size",min=10,max=25,value=15,step=1,ticks=True)
                                          ),
                                          ui.row(
                                              ui.input_slider("labelfont","Data label size",min=10,max=25,value=15,step=1,ticks=True)
                                          ),
                                          ui.row(
                                              ui.input_slider("legendfont","Legend size",min=10,max=25,value=15,step=1,ticks=True)
                                          ),
                                          ui.row(
                                              ui.input_slider("ypadding","y-axis padding for data labels",min=0,max=1,value=0.3,step=0.05,ticks=True)
                                          )
                                      )
                                     ),
                         ui.nav_panel("Column Check",
                                      ui.output_table("column_check")
                                     ),
                         ui.nav_panel("File Preview",
                                      ui.output_data_frame("filepreview")
                                      ),
                         ),icon=icon_svg("gear")
                     ),
        ui.nav_panel("ID Counts",
                     ui.navset_pill(
                         ui.nav_panel("Counts per Condition",
                                      ui.card(
                                          ui.row(
                                              ui.input_slider("idmetrics_width","Plot width",min=500,max=2000,step=100,value=1500,ticks=True),
                                              ui.input_slider("idmetrics_height","Plot height",min=500,max=2000,step=100,value=1000,ticks=True)
                                              )
                                              ),
                                      ui.input_selectize("idplotinput","Choose what metric to plot:",choices={"all":"all","proteins":"proteins","proteins2pepts":"proteins2pepts","peptides":"peptides","precursors":"precursors"},multiple=False,selected="all"),
                                      ui.output_plot("idmetricsplot")
                                    ),
                         ui.nav_panel("Average Counts",
                                      ui.card(
                                          ui.row(
                                              ui.input_slider("avgidmetrics_width","Plot width",min=500,max=2000,step=100,value=1500,ticks=True),
                                              ui.input_slider("avgidmetrics_height","Plot height",min=500,max=2000,step=100,value=1000,ticks=True)
                                              )
                                              ),
                                      ui.input_selectize("avgidplotinput","Choose what metric to plot:",choices={"all":"all","proteins":"proteins","proteins2pepts":"proteins2pepts","peptides":"peptides","precursors":"precursors"},multiple=False,selected="all"),
                                      ui.output_plot("avgidmetricsplot")
                                    ),
                         ui.nav_panel("CV Plots",
                                      ui.card(
                                          ui.row(
                                              ui.input_slider("cvplot_width","Plot width",min=100,max=2000,step=100,value=1000,ticks=True),
                                              ui.input_slider("cvplot_height","Plot height",min=100,max=2000,step=100,value=500,ticks=True)
                                              )
                                            ),
                                      ui.row(
                                          ui.input_radio_buttons("proteins_precursors_cvplot","Pick which IDs to plot",choices={"Protein":"Protein","Precursor":"Precursor"}),
                                          ui.input_switch("removetop5percent","Remove top 5%")
                                          ),
                                      ui.output_plot("cvplot")
                                      ),
                         ui.nav_panel("IDs with CV Cutoff",
                                      ui.card(
                                          ui.row(
                                              ui.input_slider("countscvcutoff_width","Plot width",min=500,max=2000,step=100,value=900,ticks=True),
                                              ui.input_slider("countscvcutoff_height","Plot height",min=500,max=2000,step=100,value=700,ticks=True)
                                            )
                                          ),
                                      ui.input_radio_buttons("proteins_precursors_idcutoffplot","Pick which IDs to plot",choices={"proteins":"proteins","precursors":"precursors"}),
                                      ui.output_plot("countscvcutoff")
                                    ),
                         ui.nav_panel("UpSet Plot",
                                      ui.card(
                                          ui.row(
                                              ui.input_slider("upsetplot_width","Plot width",min=500,max=2000,step=100,value=900,ticks=True),
                                              ui.input_slider("upsetplot_height","Plot height",min=500,max=2000,step=100,value=700,ticks=True)
                                            )
                                          ),
                                      ui.input_selectize("protein_precursor_pick","Pick which IDs to plot",choices={"Protein":"Protein","Peptide":"Peptide"}),
                                      ui.output_plot("upsetplot")
                                    )
                        ),icon=icon_svg("chart-simple")
                     ),
        ui.nav_panel("Metrics",
                     ui.navset_pill(
                         ui.nav_panel("Charge State",
                                      ui.card(
                                          ui.row(
                                              ui.input_slider("chargestate_width","Plot width",min=200,max=2000,step=100,value=1000,ticks=True),
                                              ui.input_slider("chargestate_height","Plot height",min=200,max=2000,step=100,value=500,ticks=True)
                                            )
                                          ),
                                      ui.input_radio_buttons("chargestate_condition_or_run","Plot by condition or by individual run?",choices={"condition":"condition","individual":"individual run"}),
                                      ui.output_plot("chargestateplot")
                                      ),
                         ui.nav_panel("Peptide Length",
                                      ui.card(
                                          ui.row(
                                              ui.input_slider("peptidelength_width","Plot width",min=200,max=2000,step=100,value=1000,ticks=True),
                                              ui.input_slider("peptidelength_height","Plot height",min=200,max=2000,step=100,value=500,ticks=True)
                                            )
                                          ),
                                      ui.input_radio_buttons("peptidelengths_condition_or_run","Plot by condition or by individual run?",choices={"condition":"condition","individual":"individual run"}),
                                      ui.input_radio_buttons("peplengthinput","Line plot or bar plot?",choices={"lineplot":"line plot","barplot":"bar plot"}),
                                      ui.output_ui("lengthmark_ui"),
                                      ui.output_plot("peptidelengthplot")
                                      ),
                         ui.nav_panel("Peptides per Protein",
                                      ui.card(
                                          ui.row(
                                              ui.input_slider("pepsperprotein_width","Plot width",min=200,max=2000,step=100,value=1000,ticks=True),
                                              ui.input_slider("pepsperprotein_height","Plot height",min=200,max=2000,step=100,value=500,ticks=True)
                                            )
                                          ),
                                      ui.input_radio_buttons("pepsperprotein_condition_or_run","Plot by condition or by individual run?",choices={"condition":"condition","individual":"individual run"}),
                                      ui.input_radio_buttons("pepsperproteininput","Line plot or bar plot?",choices={"lineplot":"line plot","barplot":"bar plot"}),
                                      ui.output_plot("pepsperproteinplot")
                                      ),
                         ui.nav_panel("Dynamic Range",
                                      ui.row(ui.column(5,ui.output_ui("sampleconditions_ui"),ui.input_selectize("meanmedian","Mean or median",choices={"mean":"mean","median":"median"})),
                                      ui.column(7,ui.input_numeric("top_n","Input top N proteins to display:",value=25.0,min=5.0,step=5.0))),
                                      ui.row(ui.column(5,ui.output_plot("dynamicrangeplot")),ui.column(7,ui.output_data_frame("dynamicrange_proteinrank"))),
                                      ),
                         ui.nav_panel("Data Completeness",
                                      ui.card(
                                          ui.row(
                                              ui.input_slider("datacompleteness_width","Plot width",min=200,max=2000,step=100,value=1000,ticks=True),
                                              ui.input_slider("datacompleteness_height","Plot height",min=200,max=2000,step=100,value=500,ticks=True)
                                            )
                                        ),
                                      ui.input_radio_buttons("protein_peptide","Pick what metric to plot:",choices={"proteins":"Proteins","peptides":"Peptides"}),
                                      ui.output_plot("datacompletenessplot")
                                      ),
                         ui.nav_panel("Peak Width",
                                      ui.card(
                                          ui.row(
                                              ui.input_slider("peakwidth_width","Plot width",min=200,max=2000,step=100,value=1000,ticks=True),
                                              ui.input_slider("peakwidth_height","Plot height",min=200,max=2000,step=100,value=500,ticks=True)
                                          )
                                      ),
                                      ui.output_plot("peakwidthplot")
                                      )
                        ),icon=icon_svg("chart-line")
                     ),
        ui.nav_panel("PTMs",
                     ui.navset_pill(
                         ui.nav_panel("PTMs found",
                             ui.output_ui("ptmlist_ui")
                             ),
                         ui.nav_panel("Counts per Condition",
                                      ui.card(
                                          ui.row(
                                              ui.input_slider("ptmidmetrics_width","Plot width",min=500,max=2000,step=100,value=1500,ticks=True),
                                              ui.input_slider("ptmidmetrics_height","Plot height",min=500,max=2000,step=100,value=1000,ticks=True)
                                            )
                                          ),
                                      ui.input_selectize("ptmidplotinput","Choose what metric to plot:",choices={"all":"all","proteins":"proteins","proteins2pepts":"proteins2pepts","peptides":"peptides","precursors":"precursors"},multiple=False,selected="all"),
                                      ui.output_plot("ptmidmetricsplot")
                                      ),
                         ui.nav_panel("PTM Enrichment",
                                      ui.card(
                                          ui.row(
                                              ui.input_slider("ptmenrichment_width","Plot width",min=500,max=2000,step=100,value=1500,ticks=True),
                                              ui.input_slider("ptmenrichment_height","Plot height",min=500,max=2000,step=100,value=1000,ticks=True)
                                            )
                                        ),
                                      ui.input_selectize("ptmenrichplotinput","Choose what metric to plot:",choices={"all":"all","proteins":"proteins","proteins2pepts":"proteins2pepts","peptides":"peptides","precursors":"precursors"},multiple=False,selected="all"),
                                      ui.output_plot("ptmenrichment")
                                      ),
                         ui.nav_panel("CV Plots",
                                      ui.card(
                                          ui.row(
                                              ui.input_slider("ptmcvplot_width","Plot width",min=500,max=2000,step=100,value=1000,ticks=True),
                                              ui.input_slider("ptmcvplot_height","Plot height",min=500,max=2000,step=100,value=500,ticks=True)
                                            )
                                        ),
                                      ui.row(
                                          ui.input_radio_buttons("ptm_proteins_precursors","Pick which IDs to plot",choices={"Protein":"Protein","Precursor":"Precursor"}),
                                          ui.input_switch("ptm_removetop5percent","Remove top 5%")
                                          ),
                                      ui.output_plot("ptm_cvplot")
                                      ),
                         ui.nav_panel("PTMs per Precursor",
                                      ui.card(
                                          ui.row(
                                              ui.input_slider("ptmsperprecursor_width","Plot width",min=500,max=2000,step=100,value=1000,ticks=True),
                                              ui.input_slider("ptmsperprecursor_height","Plot height",min=500,max=2000,step=100,value=600,ticks=True)
                                            )
                                          ),
                                      ui.input_slider("barwidth","Bar width",min=0.1,max=1,step=0.05,value=0.25,ticks=True),
                                      ui.output_plot("ptmsperprecursor")
                                      )
                            ),icon=icon_svg("binoculars")
                     ),
        ui.nav_panel("Heatmaps",
                     ui.navset_pill(
                        ui.nav_panel("RT, m/z, IM Heatmaps",
                                     ui.input_slider("heatmap_numbins","Number of bins",min=10,max=250,value=100,step=10,ticks=True),
                                     ui.input_radio_buttons("conditiontype","Plot by individual replicate or by condition",choices={"replicate":"By replicate","condition":"By condition"}),
                                     ui.output_ui("cond_rep_list_heatmap"),
                                     ui.output_plot("replicate_heatmap")
                                     ),
                        ui.nav_panel("Charge/PTM Precursor Heatmap",
                                     ui.card(
                                         ui.input_file("diawindow_upload","Upload DIA windows as a .csv:")
                                         ),
                                     ui.row(
                                         ui.column(4,
                                                   ui.input_radio_buttons("windows_choice","Choose DIA windows to overlay:",choices={"imported":"Imported DIA windows","lubeck":"Lubeck DIA","phospho":"Phospho DIA","None":"None"},selected="None"),
                                                   ui.input_slider("chargeptm_numbins_x","Number of m/z bins",min=10,max=250,value=100,step=10,ticks=True),
                                                   ui.input_slider("chargeptm_numbins_y","Number of mobility bins",min=10,max=250,value=100,step=10,ticks=True),
                                                   ui.output_ui("chargestates_chargeptmheatmap_ui"),
                                                   ui.output_ui("ptm_chargeptmheatmap_ui"),
                                                   ),
                                         ui.column(6,
                                                   ui.output_plot("chargeptmheatmap")
                                                   )
                                             ),
                                     ),
                        ui.nav_panel("Charge/PTM Precursor Scatter",
                                     ui.card(
                                         ui.row(
                                            ui.input_slider("chargeptmscatter_width","Plot width",min=500,max=2000,step=100,value=800,ticks=True),
                                            ui.input_slider("chargeptmscatter_height","Plot height",min=300,max=2000,step=100,value=600,ticks=True)
                                            )
                                        ),
                                     ui.row(
                                         ui.input_radio_buttons("charge_or_ptm","Plot based on charge or PTM?",choices={"charge":"charge","ptm":"ptm"}),
                                         ui.output_ui("charge_ptm_dropdown")
                                         ),
                                     ui.output_plot("chargeptmscatter")
                                     ),
                        ui.nav_panel("#IDs vs RT",
                                     ui.card(
                                         ui.row(
                                            ui.input_slider("idsvsrt_width","Plot width",min=500,max=2000,step=100,value=1000,ticks=True),
                                            ui.input_slider("idsvsrt_height","Plot height",min=300,max=2000,step=100,value=500,ticks=True)
                                            )
                                        ),
                                     ui.output_ui("binslider_ui"),
                                     ui.output_plot("ids_vs_rt")
                                     ),
                        ui.nav_panel("Venn Diagram of IDs",
                                     ui.output_ui("cond_rep_list_venn1"),
                                     ui.output_ui("cond_rep_list_venn2"),
                                     ui.input_selectize("vennpick","Pick what metric to compare:",choices={"proteins":"proteins","peptides":"peptides","precursors":"precursors"}),
                                     ui.output_plot("venndiagram")
                                     ),
                        ),icon=icon_svg("chart-area")
                     ),
        ui.nav_panel("PCA",
                     ui.navset_pill(
                         ui.nav_panel("PCA",
                                    ui.card(
                                        ui.row(
                                            ui.input_slider("pca_width","Plot width",min=200,max=2000,step=100,value=1000,ticks=True),
                                            ui.input_slider("pca_height","Plot height",min=200,max=2000,step=100,value=500,ticks=True)
                                            )
                                          ),
                                      ui.output_plot("pca_plot")
                                      )
                      ),icon=icon_svg("network-wired")
                     ),
        ui.nav_panel("Mixed Proteome",
                      ui.navset_pill(
                             ui.nav_panel("Info",
                                          ui.input_text("organisminput","Input organism names in all caps separated by a space (e.g. HUMAN YEAST ECOLI):"),
                                          ui.output_text_verbatim("organisminput_readout"),
                                          ui.input_radio_buttons("coloroptions_sumint","Use matplotlib tableau colors or blues/grays?",choices={"matplot":"matplotlib tableau","bluegray":"blues/grays"})
                                          ),
                             ui.nav_panel("Summed Intensities",
                                          ui.card(
                                              ui.row(
                                                  ui.input_slider("summedintensities_width","Plot width",min=500,max=2000,step=100,value=1000,ticks=True),
                                                  ui.input_slider("summedintensities_height","Plot height",min=500,max=2000,step=100,value=700,ticks=True)
                                              )
                                            ),
                                          ui.output_plot("summedintensities")
                                          ),
                             ui.nav_panel("Counts per Organism",
                                          ui.card(
                                              ui.row(
                                                  ui.input_slider("countsperorganism_width","Plot width",min=500,max=2000,step=100,value=1000,ticks=True),
                                                  ui.input_slider("countsperorganism_height","Plot height",min=500,max=2000,step=100,value=700,ticks=True)
                                                )
                                            ),
                                          ui.input_selectize("countsplotinput","Choose what metric to plot:",choices={"proteins":"proteins","peptides":"peptides","precursors":"precursors"},multiple=False),
                                          ui.output_plot("countsperorganism")
                                          ),
                             ui.nav_panel("Quant Ratios",
                                          ui.row(
                                              ui.column(4,
                                                        ui.output_ui("referencecondition"),ui.output_ui("testcondition"),ui.output_text_verbatim("organismreminder")
                                                        ),
                                              ui.column(4,
                                                        ui.input_text("referenceratio","Input ratios for each organism in the reference condition separated by a space: "),ui.output_text_verbatim("referenceratio_readout"),
                                                        ui.input_text("testratio","Input ratios for each organism in the test condition separated by a space: "),ui.output_text_verbatim("testratio_readout"),
                                                        ui.output_text("expectedratios_note")
                                                        ),
                                              ui.column(3,
                                                        ui.input_slider("plotrange","Plot Range",min=-10,max=10,value=[-2,2],step=0.5,ticks=True,width="400px",drag_range=True),
                                                        ui.input_switch("plotrange_switch","Use slider for y-axis range"),
                                                        ui.input_slider("cvcutofflevel","CV Cutoff Level (%)",min=10,max=50,value=20,step=10,ticks=True,width="400px"),
                                                        ui.input_switch("cvcutoff_switch","Include CV cutoff?")),
                                                        ),
                                          ui.output_plot("quantratios")
                                          )
                            ),icon=icon_svg("flask")
                      ),
        ui.nav_panel("PRM",
                     ui.navset_pill(
                        ui.nav_panel("PRM List",
                                     ui.input_file("prm_list","Upload Peptide List:")
                                     ),
                        ui.nav_panel("PRM Table",
                                     ui.card(
                                         ui.row(
                                             ui.input_text("isolationwidth_input","m/z isolation width:"),
                                             ui.input_text("rtwindow_input","Retention time window (s):"),
                                             ui.input_text("imwindow_input","Ion mobility window (1/k0):")
                                             )
                                     ),
                                     ui.download_button("prm_table_download","Download PRM Table",width="300px",icon=icon_svg("file-arrow-down")),
                                     ui.output_data_frame("prm_table")
                                     ),
                        ui.nav_panel("PRM Peptides - Individual Tracker",
                                     ui.card(
                                        ui.row(
                                            ui.input_slider("prmpeptracker_width","Plot width",min=500,max=2000,step=100,value=1000,ticks=True),
                                            ui.input_slider("prmpeptracker_height","Plot height",min=500,max=2000,step=100,value=700,ticks=True)
                                        )
                                     ),
                                     ui.output_ui("prmpeptracker_pick"),
                                     ui.output_plot("prmpeptracker_plot")
                                     ),
                        ui.nav_panel("PRM Peptides - Intensity Across Runs",
                                     ui.card(
                                        ui.row(
                                            ui.input_slider("prmpepintensity_width","Plot width",min=500,max=2000,step=100,value=1000,ticks=True),
                                            ui.input_slider("prmpepintensity_height","Plot height",min=500,max=2000,step=100,value=700,ticks=True)
                                        )
                                     ),
                                     ui.output_plot("prmpepintensity_plot"),
                                     ),
                        # ui.nav_panel("Manual Peptide Tracker",
                        #              ui.row(
                        #                  ui.input_text("tracked_peptide","Input stripped peptide sequence:")
                        #                  ),
                        #                  ui.card(
                        #                      ui.output_plot("peptide_intensity")
                        #                      ),
                        #                  ui.card(
                        #                      ui.output_plot("peptide_replicates")
                        #                      )
                        #             )
                        ),icon=icon_svg("wand-sparkles")
                    ),
        ui.nav_panel("Dilution Series",
                     ui.navset_pill(
                         ui.nav_panel("Dilution Ratios",
                                      ui.card(
                                          ui.row(
                                            ui.input_slider("dilutionseries_width","Plot width",min=500,max=2000,step=100,value=1000,ticks=True),
                                            ui.input_slider("dilutionseries_height","Plot height",min=500,max=2000,step=100,value=700,ticks=True)
                                            )
                                            ),
                                      ui.output_ui("normalizingcondition"),
                                      ui.output_plot("dilutionseries_plot")
                                    )
                     ),icon=icon_svg("vials")
                    ),
        ui.nav_panel("Raw Data",
                     ui.navset_pill(
                         ui.nav_panel("Multi-File Import",
                                      ui.input_text_area("rawfile_input","Paste the path for each .d file you want to upload (note: do not leave whitespace at the end):",width="1500px",autoresize=True,placeholder="ex - C:\\Users\\Data\\K562_500ng_1_Slot1-49_1_3838.d")
                                      ),
                         ui.nav_panel("TIC Plot",
                                      ui.card(
                                          ui.row(
                                              ui.input_slider("tic_width","Plot width",min=500,max=2000,step=100,value=1500,ticks=True),
                                              ui.input_slider("tic_height","Plot height",min=500,max=2000,step=100,value=600,ticks=True)
                                            )
                                          ),
                                      ui.card(
                                          ui.row(
                                              ui.output_ui("rawfile_checkboxes_tic")),
                                          ui.row(
                                              ui.input_switch("stacked_tic","Stack TIC Plots"))
                                          ),
                                      ui.output_plot("TIC_plot")
                                      ),
                         ui.nav_panel("BPC Plot",
                                      ui.card(
                                          ui.row(
                                              ui.input_slider("bpc_width","Plot width",min=500,max=2000,step=100,value=1500,ticks=True),
                                              ui.input_slider("bpc_height","Plot height",min=500,max=2000,step=100,value=600,ticks=True)
                                            )
                                          ),
                                      ui.card(
                                          ui.row(
                                              ui.output_ui("rawfile_checkboxes_bpc")),
                                          ui.row(
                                              ui.input_switch("stacked_bpc","Stack BPC Plots"))
                                          ),
                                      ui.output_plot("BPC_plot")
                                      ),
                         ui.nav_panel("Accumulation Time",
                                      ui.card(
                                          ui.row(
                                              ui.input_slider("accutime_width","Plot width",min=500,max=2000,step=100,value=1500,ticks=True),
                                              ui.input_slider("accutime_height","Plot height",min=500,max=2000,step=100,value=600,ticks=True)
                                            )
                                          ),
                                      ui.card(
                                          ui.row(
                                              ui.output_ui("rawfile_checkboxes_accutime")),
                                          ui.row(
                                              ui.input_switch("stacked_accutime","Stack Plots"))
                                          ),
                                      ui.output_plot("accutime_plot")
                                      ),
                         ui.nav_panel("EIC Plot",
                                      ui.card(
                                          ui.row(ui.column(4,
                                                           ui.input_text("eic_mz_input","Input m/z for EIC:"),
                                                           ui.input_text("eic_ppm_input","Input mass error (ppm) for EIC:"),
                                                           ),
                                                 ui.column(4,
                                                           ui.input_switch("include_mobility","Include mobility in EIC"),
                                                           ui.output_ui("mobility_input")
                                                           ),
                                                ui.output_ui("rawfile_buttons_eic")
                                            ),
                                          ui.input_action_button("load_eic","Load EIC",class_="btn-primary")
                                          ),
                                      ui.card(
                                          ui.row(
                                              ui.input_slider("eic_width","Plot width",min=500,max=2000,step=100,value=1500,ticks=True),
                                              ui.input_slider("eic_height","Plot height",min=200,max=2000,step=100,value=600,ticks=True)
                                            )
                                          ),
                                      ui.output_plot("eic")
                                      ),
                         ui.nav_panel("EIM Plot",
                                      ui.card(
                                          ui.row(ui.column(4,
                                                           ui.input_text("eim_mz_input","Input m/z for EIM:"),
                                                           ui.input_text("eim_ppm_input","Input mass error (ppm) for EIM:"),
                                                           ),
                                                ui.output_ui("rawfile_buttons_eim")
                                            ),
                                          ui.input_action_button("load_eim","Load EIM",class_="btn-primary")
                                          ),
                                      ui.card(
                                          ui.row(
                                              ui.input_slider("eim_width","Plot width",min=500,max=2000,step=100,value=1500,ticks=True),
                                              ui.input_slider("eim_height","Plot height",min=200,max=2000,step=100,value=600,ticks=True)
                                            )
                                          ),
                                      ui.output_plot("eim")
                                      ),
                         ),icon=icon_svg("desktop")
                     ),
        ui.nav_panel("Export Tables",
                     ui.navset_pill(
                         ui.nav_panel("Export Tables",
                                      ui.card(
                                          ui.card_header("Table of Peptide IDs"),
                                          ui.download_button("peptidelist","Download Peptide IDs",width="300px",icon=icon_svg("file-arrow-down")),
                                          ),
                                      ui.card(
                                          ui.card_header("Table of Protein ID Metrics and CVs"),
                                          ui.download_button("proteinidmetrics_download","Download Protein ID Metrics",width="300px",icon=icon_svg("file-arrow-down"))
                                          ),
                                      ui.card(
                                          ui.card_header("Table of Precursor ID Metrics and CVs"),
                                          ui.download_button("precursoridmetrics_download","Download Precursor ID Metrics",width="300px",icon=icon_svg("file-arrow-down"))
                                          ),
                                      ui.card(
                                          ui.card_header("List of MOMA Precursors"),
                                          ui.row(
                                              ui.column(4,
                                                        ui.output_ui("cond_rep_list"),
                                                        ui.download_button("moma_download","Download MOMA List",width="300px",icon=icon_svg("file-arrow-down"))
                                                        ),
                                              ui.column(4,
                                                        ui.input_slider("rttolerance","Retention time tolerance (%)",min=0.5,max=10,value=1,step=0.5,ticks=True),
                                                        ui.input_slider("mztolerance","m/z tolerance (m/z):",min=0.0005,max=0.1,value=0.005,step=0.0005,ticks=True)
                                              )
                                          )
                                          ),
                                      ui.card(
                                          ui.card_header("List of PTMs per Precursor"),
                                          ui.download_button("ptmlist_download","Download Precursor PTMs",width="300px",icon=icon_svg("file-arrow-down"))
                                          )
                                      )
                                ),icon=icon_svg("file-export")
                     ),
        ui.nav_panel("Glycoproteomics",
                     ui.navset_pill(
                         ui.nav_panel("Glyco ID Metrics",
                                      ui.card(
                                          ui.row(
                                              ui.input_slider("glycoIDsplot_width","Plot width",min=200,max=2000,step=100,value=1000,ticks=True),
                                              ui.input_slider("glycoIDsplot_height","Plot height",min=200,max=2000,step=100,value=500,ticks=True)
                                            )
                                          ),
                                      ui.output_plot("glycoIDsplot")
                                      ),
                         ui.nav_panel("Glyco ID Tables",
                                      ui.row(
                                          ui.column(3,
                                              ui.download_button("glycoproteins_download","Download Glycoprotein IDs",width="300px",icon=icon_svg("file-arrow-down")),
                                              ui.output_data_frame("glycoproteins_df_view")
                                          ),
                                          ui.column(4,
                                              ui.download_button("glycopeptides_download","Download Glycopeptide IDs",width="300px",icon=icon_svg("file-arrow-down")),
                                              ui.output_data_frame("glycopeptides_df_view")
                                          ),
                                          ui.column(4,
                                              ui.download_button("glycoPSMs_download","Download GlycoPSM IDs",width="300px",icon=icon_svg("file-arrow-down")),
                                              ui.output_data_frame("glycoPSMs_df_view")
                                          ),
                                      ),
                                      ),
                         ui.nav_panel("Glycan Tracker",
                                      ui.card(
                                          ui.row(
                                              ui.input_slider("glycomodIDsplot_width","Plot width",min=200,max=2000,step=100,value=1000,ticks=True),
                                              ui.input_slider("glycomodIDsplot_height","Plot height",min=200,max=2000,step=100,value=500,ticks=True)
                                            )
                                          ),
                                      ui.row(
                                          ui.output_ui("glycomodlist_ui"),
                                          ui.input_radio_buttons("counts_vs_enrich","Show counts or enrichment %?",choices={"counts":"Counts","enrich":"Enrichment %"})
                                          ),
                                      ui.output_plot("glycomod_IDs")
                                      ),
                         ui.nav_panel("Peptide Tracker",
                                      ui.row(
                                          ui.column(6,
                                                    ui.download_button("selected_glyco_download","Download PSMs for Selected Peptide",width="400px",icon=icon_svg("file-arrow-down")),
                                                    ui.output_ui("glyco_peplist")
                                                    )
                                             ),
                                      ui.output_data_frame("selected_glyco_peplist")
                                      ),
                         ui.nav_panel("Precursor Scatterplot",
                                      ui.card(
                                          ui.row(
                                              ui.input_slider("glycoscatter_width","Plot width",min=200,max=2000,step=100,value=1000,ticks=True),
                                              ui.input_slider("glycoscatter_height","Plot height",min=200,max=2000,step=100,value=500,ticks=True)
                                            )
                                          ),
                                      ui.output_plot("glycoscatter")
                                      ),
                                ),icon=icon_svg("cubes-stacked")
                     ),
    widths=(2,8)
    ),
    theme=theme.cerulean()
)
#endregion

# =============================================================================
# Server
# =============================================================================

def server(input: Inputs, output: Outputs, session: Session):

# ============================================================================= UI calls for use around the app
#region

    #render ui call for dropdown calling sample condition names
    @render.ui
    def sampleconditions_ui():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
        opts=sampleconditions
        return ui.input_selectize("conditionname","Pick sample condition",choices=opts)

    #render ui call for dropdown calling replicate number
    @render.ui
    def replicates_ui():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
        opts=np.arange(1,max(repspercondition)+1,1)
        return ui.input.selectize("replicate","Replicate number",opts)

    #render ui call for dropdown calling Cond_Rep column
    @render.ui
    def cond_rep_list():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
        opts=resultdf["Cond_Rep"].tolist()
        return ui.input_selectize("cond_rep","Pick run:",choices=opts)    

#endregion

# ============================================================================= File Import, Metadata Generation, Updating searchoutput Based on Metadata
#region

    #import search report file
    @reactive.calc
    def inputfile():
        if input.searchreport() is None:
            return pd.DataFrame()
        searchoutput=pd.read_csv(input.searchreport()[0]["datapath"],sep="\t")
        if input.software()=="diann":
            searchoutput.rename(columns={"Run":"R.FileName"},inplace=True)
            searchoutput.insert(1,"R.Condition","")
            searchoutput.insert(2,"R.Replicate","")
            searchoutput["EG.PeakWidth"]=searchoutput["RT.Stop"]-searchoutput["RT.Start"]
            searchoutput.drop(columns=["File.Name","PG.Normalized","PG.MaxLFQ","Genes.Quantity",
                                        "Genes.Normalised","Genes.MaxLFQ","Genes.MaxLFQ.Unique","Precursor.Id",
                                        "PEP","Global.Q.Value","Protein.Q.Value","Global.PG.Q.Value","GG.Q.Value",
                                        "Translated.Q.Value","Precursor.Translated","Translated.Quality","Ms1.Translated",
                                        "Quantity.Quality","RT.Stop","RT.Start","iRT","Predicted.iRT",
                                        "First.Protein.Description","Lib.Q.Value","Lib.PG.Q.Value","Ms1.Profile.Corr",
                                        "Ms1.Area","Evidence","Spectrum.Similarity","Averagine","Mass.Evidence",
                                        "Decoy.Evidence","Decoy.CScore","Fragment.Quant.Raw","Fragment.Quant.Corrected",
                                        "Fragment.Correlations","MS2.Scan","iIM","Predicted.IM",
                                        "Predicted.iIM"],inplace=True,errors='ignore')
            searchoutput.rename(columns={#"Run":"R.FileName",
                        "Protein.Group":"PG.ProteinGroups",
                        "Protein.Ids":"PG.ProteinAccessions",
                        "Protein.Names":"PG.ProteinNames",
                        "PG.Quantity":"PG.MS2Quantity",
                        "Genes":"PG.Genes",
                        "Stripped.Sequence":"PEP.StrippedSequence",
                        "Modified.Sequence":"EG.ModifiedPeptide",
                        "Precursor.Charge":"FG.Charge",
                        "Q.Value":"EG.Qvalue",
                        "PG.Q.Value":"PG.Qvalue",
                        "Precursor.Quantity":"FG.MS2Quantity",
                        "Precursor.Normalised":"FG.MS2RawQuantity",
                        "RT":"EG.ApexRT",
                        "Predicted.RT":"EG.RTPredicted",
                        "CScore":"EG.Cscore",
                        "IM":"EG.IonMobility",
                        "Proteotypic":"PEP.IsProteotypic"},inplace=True)
            searchoutput["EG.ModifiedPeptide"]=searchoutput["EG.ModifiedPeptide"].str.replace("(","[")
            searchoutput["EG.ModifiedPeptide"]=searchoutput["EG.ModifiedPeptide"].str.replace(")","]")
            searchoutput["EG.ModifiedPeptide"]=searchoutput["EG.ModifiedPeptide"].replace({
                    "UniMod:1":"Acetyl (Protein N-term)",
                    "UniMod:4":"Carbamidomethyl (C)",
                    "UniMod:21":"Phospho (STY)",
                    "UniMod:35":"Oxidation (M)"},regex=True)
        if input.software()=="ddalibrary":
            searchoutput.rename(columns={"ReferenceRun":"R.FileName"},inplace=True)
            searchoutput.insert(1,"R.Condition","")
            searchoutput.insert(2,"R.Replicate","")
            searchoutput=searchoutput.rename(columns={"ReferenceRun":"R.FileName",
                            "PrecursorCharge":"FG.Charge",
                            "ModifiedPeptide":"EG.ModifiedPeptide",
                            "StrippedPeptide":"PEP.StrippedSequence",
                            "IonMobility":"EG.IonMobility",
                            "PrecursorMz":"FG.PrecMz",
                            "ReferenceRunMS1Response":"FG.MS2Quantity",
                            "Protein Name":"PG.ProteinNames"})
        if input.software()=="timsdiann":
            searchoutput.rename(columns={"File.Name":"R.FileName"},inplace=True)
            searchoutput.insert(1,"R.Condition","")
            searchoutput.insert(2,"R.Replicate","")
            searchoutput["EG.PeakWidth"]=searchoutput["RT.Stop"]-searchoutput["RT.Start"]
            searchoutput.drop(columns=["Run","PG.Normalised","Genes.Quantity",
                                       "Genes.Normalised","Genes.MaxLFQ","Genes.MaxLFQ.Unique","PG.MaxLFQ",
                                       "Precursor.Id","Protein.Q.Value","GG.Q.Value","Label.Ratio",
                                       "Quantity.Quality","RT.Start","RT.Stop","iRT","Predicted.iRT",
                                       "First.Protein.Description","Lib.Q.Value","Ms1.Profile.Corr",
                                       "Ms1.Corr.Sum","Ms1.Area","Evidence","Decoy.Evidence","Decoy.CScore",
                                       "Fragment.Quant.Raw","Fragment.Quant.Corrected","Fragment.Correlations",
                                       "MS2.Scan","Precursor.FWHM","Precursor.Error.Ppm","Corr.Precursor.Error.Ppm",
                                       "Data.Points","Ms1.Iso.Corr.Sum","Library.Precursor.Mz","Corrected.Precursor.Mz",
                                       "Precursor.Calibrated.Mz","Fragment.Info","Fragment.Calibrated.Mz","Lib.1/K0"],inplace=True,errors='ignore')

            searchoutput.rename(columns={"Protein.Group":"PG.ProteinGroups",
                                         "Protein.Ids":"PG.ProteinAccessions",
                                         "Protein.Names":"PG.ProteinNames",
                                         "Genes":"PG.Genes",
                                         "PG.Quantity":"PG.MS2Quantity",
                                         "Modified.Sequence":"EG.ModifiedPeptide",
                                         "Stripped.Sequence":"PEP.StrippedSequence",
                                         "Precursor.Charge":"FG.Charge",
                                         "Q.Value":"EG.Qvalue",
                                         "PG.Q.Value":"PG.Qvalue",
                                         "Precursor.Quantity":"FG.MS2Quantity",
                                         "Precursor.Normalized":"FG.MS2RawQuantity",
                                         "RT":"EG.ApexRT",
                                         "Predicted.RT":"EG.RTPredicted",
                                         "CScore":"EG.CScore",
                                         "Proteotypic":"PEP.IsProteotypic",
                                         "Exp.1/K0":"EG.IonMobility"},inplace=True)

            searchoutput["EG.ModifiedPeptide"]=searchoutput["EG.ModifiedPeptide"].str.replace("(UniMod:7)","")
            searchoutput["EG.ModifiedPeptide"]=searchoutput["EG.ModifiedPeptide"].str.replace("(","[")
            searchoutput["EG.ModifiedPeptide"]=searchoutput["EG.ModifiedPeptide"].str.replace(")","]")

            searchoutput["EG.ModifiedPeptide"]=searchoutput["EG.ModifiedPeptide"].replace({
                    "UniMod:1":"Acetyl (Protein N-term)",
                    "UniMod:4":"Carbamidomethyl (C)",
                    "UniMod:21":"Phospho (STY)",
                    "UniMod:35":"Oxidation (M)"},regex=True)
        if input.software()=="fragpipe":
            searchoutput.rename(columns={"Spectrum File":"R.FileName"},inplace=True)
            searchoutput.insert(1,"R.Condition","")
            searchoutput.insert(2,"R.Replicate","")

            searchoutput.drop(columns=["Spectrum","Extended Peptide","Prev AA","Next AA","Peptide Length",
                                    "Observed Mass","Calibrated Observed Mass","Calibrated Observed M/Z",
                                    "Calculated Peptide Mass","Calculated M/Z","Delta Mass",#"SpectralSim",
                                    #"RTScore",
                                    "Expectation","Hyperscore","Nextscore",#"Probability",
                                    "Number of Enzymatic Termini","Number of Missed Cleavages","Protein Start",
                                    "Protein End","Assigned Modifications","Observed Modifications",
                                    "Purity","Is Unique","Protein","Protein Description","Mapped Genes","Mapped Proteins"],inplace=True,errors='ignore')

            searchoutput.rename(columns={"Peptide":"PEP.StrippedSequence",
                                        "Modified Peptide":"EG.ModifiedPeptide",
                                        "Charge":"FG.Charge",
                                        "Retention":"EG.ApexRT",
                                        "Observed M/Z":"FG.PrecMz",
                                        "Ion Mobility":"EG.IonMobility",
                                        "Protein ID":"PG.ProteinGroups",
                                        "Entry Name":"PG.ProteinNames",
                                        "Gene":"PG.Genes",
                                        "Intensity":"FG.MS2Quantity"
                                        },inplace=True)

            searchoutput["EG.ApexRT"]=searchoutput["EG.ApexRT"]/60
            searchoutput["EG.ModifiedPeptide"]=searchoutput["EG.ModifiedPeptide"].replace({
                "n":"",
                "147":"Oxidation (M)",
                "222":"Carbamidomethyl (C)",
                "43":"[Acetyl (Protein N-term)]",
                "111":""},regex=True)

            peps=searchoutput["PEP.StrippedSequence"].tolist()
            modpeps=searchoutput["EG.ModifiedPeptide"].tolist()
            for i in range(len(peps)):
                if type(modpeps[i])!=str:
                    modpeps[i]=peps[i]
                else:
                    modpeps[i]=modpeps[i]
            searchoutput["EG.ModifiedPeptide"]=modpeps
        if input.software()=="fragpipe_glyco":
            searchoutput.rename(columns={"Spectrum File":"R.FileName"},inplace=True)
            searchoutput.insert(1,"R.Condition","")
            searchoutput.insert(2,"R.Replicate","")

            searchoutput.drop(columns=["Spectrum","Extended Peptide","Prev AA","Next AA","Peptide Length","Observed Mass",  
                    "Calibrated Observed Mass","Calibrated Observed M/Z","Calculated Peptide Mass",
                    "Calculated M/Z","Delta Mass","Expectation","Hyperscore","Nextscore","Probability",
                    "Number of Enzymatic Termini","Number of Missed Cleavages","Protein Start","Protein End",
                    "MSFragger Localization","Number Best Positions","Shifted Only Position Scores",
                    "Shifted Only Position Ions","Score Best Position","Ions Best Position",
                    "Score Second Best Position","Ions Second Best Position","Score All Unshifted",
                    "Ions All Unshifted","Score Shifted Best Position","Ions Shifted Best Position",
                    "Score Shifted All Positions","Ions Shifted All Positions","Purity","Protein",
                    "Mapped Genes","Mapped Proteins"],inplace=True,errors='ignore')

            searchoutput.rename(columns={"Peptide":"PEP.StrippedSequence",
                                        "Modified Peptide":"EG.ModifiedPeptide",
                                        "Charge":"FG.Charge",
                                        "Retention":"EG.ApexRT",
                                        "Observed M/Z":"FG.PrecMz",
                                        "Ion Mobility":"EG.IonMobility",
                                        "Protein ID":"PG.ProteinGroups",
                                        "Entry Name":"PG.ProteinNames",
                                        "Gene":"PG.Genes"
                                        },inplace=True)
            
            if len(searchoutput["Intensity"].drop_duplicates())==1:
                searchoutput.drop(columns=["Intensity"],inplace=True)
            else:
                searchoutput.rename(columns={"Intensity":"FG.MS2Quantity"},inplace=True)

            searchoutput["EG.ApexRT"]=searchoutput["EG.ApexRT"]/60
            searchoutput["Is Unique"]=searchoutput["Is Unique"].astype(str)

        return searchoutput
    
    #render the metadata table in the window
    @render.data_frame
    def metadata_table():
        if input.use_uploaded_metadata()==True:
            metadata=inputmetadata()
            if metadata is None:
                metadata=pd.DataFrame(columns=["R.FileName","R.Condition","R.Replicate","remove"])
            metadata=metadata.drop(columns=["order","Concentration"])
        else:
            searchoutput=inputfile()
            if input.searchreport() is None:
                metadata=pd.DataFrame(columns=["R.FileName","R.Condition","R.Replicate","remove"])#"order","remove","Concentration"])
                return render.DataGrid(metadata,width="100%")
            metadata=pd.DataFrame(searchoutput[["R.FileName","R.Condition","R.Replicate"]]).drop_duplicates().reset_index(drop=True)
            #metadata["order"]=metadata.apply(lambda _: '', axis=1)
            metadata["remove"]=metadata.apply(lambda _: '', axis=1)
            #metadata["Concentration"]=metadata.apply(lambda _: '', axis=1)

        return render.DataGrid(metadata,editable=True,width="100%")

    @render.data_frame
    def metadata_condition_table():
        if input.use_uploaded_metadata()==True:
            metadata=inputmetadata()
            if metadata is None:
                metadata_condition=pd.DataFrame(columns=["R.Condition","order","Concentration"])
            if input.remove()==True:
                metadata=metadata[metadata.remove !="x"]
            metadata_condition=pd.DataFrame()
            metadata_condition["R.Condition"]=metadata["R.Condition"].drop_duplicates()
            metadata_condition["order"]=metadata["order"].drop_duplicates()
            metadata_condition["Concentration"]=metadata["Concentration"].drop_duplicates()
        else:
            metadata=metadata_table.data_view()
            if input.searchreport() is None:
                metadata_condition=pd.DataFrame(columns=["R.Condition","order","Concentration"])
                return render.DataGrid(metadata_condition,width="100%")
            if input.remove()==True:
                metadata=metadata[metadata.remove !="x"]
            metadata_condition=pd.DataFrame(metadata[["R.Condition"]]).drop_duplicates().reset_index(drop=True)
            metadata_condition["order"]=metadata_condition.apply(lambda _: '', axis=1)
            metadata_condition["Concentration"]=metadata_condition.apply(lambda _: '', axis=1)

        return render.DataGrid(metadata_condition,editable=True,width="100%")

    #give a reminder for what to do with search reports from different software
    @render.text
    def metadata_reminder():
        if input.software()=="spectronaut":
            return "Spectronaut: Make sure to use Shiny report format when exporting search results"
        if input.software()=="diann":
            return "DIA-NN: Make sure to fill out R.Condition and R.Replicate columns in the metadata"
        if input.software()=="ddalibrary":
            return "DDA Library: DDA libraries have limited functionality, can only plot ID metrics"
        if input.software()=="timsdiann":
            return "BPS tims-DIANN: to access results file, unzip the bps_timsDIANN folder, open the processing-run folder and its subfolder, then unzip the tims-diann.result folder. Upload the results.tsv and then make sure to fill out R.Condition and R.Replicate columns in the metadata"
        if input.software()=="fragpipe":
            return "FragPipe: Make sure to fill out R.Condition and R.Replicate columns in the metadata"
        if input.software()=="fragpipe_glyco":
            return "FragPipe (Glyco): Make sure to fill out R.Condition and R.Replicate columns in the metadata. Use the Glycoproteomics tab for processing"
    
    #download metadata table as shown
    @render.download(filename="metadata_"+str(date.today())+".csv")
    def metadata_download():
        metadata=metadata_table.data_view()
        metadata_condition=metadata_condition_table.data_view()

        orderlist=[]
        concentrationlist=[]
        #metadata_fordownload=metadata
        metadata_fordownload=pd.DataFrame()
        for run in metadata_condition["R.Condition"]:
            fileindex=metadata_condition[metadata_condition["R.Condition"]==run].index.values[0]
            orderlist.append([metadata_condition["order"][fileindex]]*len(metadata[metadata["R.Condition"]==run]))
            concentrationlist.append([metadata_condition["Concentration"][fileindex]]*len(metadata[metadata["R.Condition"]==run]))
        metadata_fordownload["R.FileName"]=metadata["R.FileName"]
        metadata_fordownload["R.Condition"]=metadata["R.Condition"]
        metadata_fordownload["R.Replicate"]=metadata["R.Replicate"]
        metadata_fordownload["remove"]=metadata["remove"]
        metadata_fordownload["order"]=list(itertools.chain(*orderlist))
        metadata_fordownload["Concentration"]=list(itertools.chain(*concentrationlist))
        with io.BytesIO() as buf:
            metadata_fordownload.to_csv(buf,index=False)
            yield buf.getvalue()

    #upload filled out metadata table
    @reactive.calc
    def inputmetadata():
        if input.metadata_upload() is None:
            metadata=pd.DataFrame(columns=["R.FileName","R.Condition","R.Replicate","remove"])
            return metadata
        else:
            metadata=pd.read_csv(input.metadata_upload()[0]["datapath"],sep=",")
        return metadata

    #update the searchoutput df to match how we edited the metadata sheet
    @reactive.calc
    @reactive.event(input.rerun_metadata,ignore_none=False)
    def metadata_update():
        searchoutput=inputfile()
        metadata=metadata_table.data_view()
        metadata_condition=metadata_condition_table.data_view()

        if input.condition_names()==True:
            RConditionlist=[]
            RReplicatelist=[]
            for run in searchoutput["R.FileName"].drop_duplicates().tolist():
                fileindex=metadata[metadata["R.FileName"]==run].index.values[0]
                RConditionlist.append([metadata["R.Condition"][fileindex]]*len(searchoutput.set_index("R.FileName").loc[run]))
                RReplicatelist.append([metadata["R.Replicate"][fileindex]]*len(searchoutput.set_index("R.FileName").loc[run]))
            searchoutput["R.Condition"]=list(itertools.chain(*RConditionlist))
            searchoutput["R.Replicate"]=list(itertools.chain(*RReplicatelist))
            searchoutput["R.Replicate"]=searchoutput["R.Replicate"].astype(int)

        if input.remove()==True:
            editedmetadata=metadata[metadata.remove !="x"]
            searchoutput=searchoutput.set_index("R.FileName").loc[editedmetadata["R.FileName"].tolist()].reset_index()

        if input.reorder()==True:
            metadata_condition["order"]=metadata_condition["order"].astype(int)
            sortedmetadata_bycondition=metadata_condition.sort_values(by="order").reset_index(drop=True)
            searchoutput=searchoutput.set_index("R.Condition").loc[sortedmetadata_bycondition["R.Condition"].tolist()].reset_index()

        if input.concentration()==True:
            concentrationlist=[]
            for run in searchoutput["R.Condition"].drop_duplicates().tolist():
                fileindex=metadata_condition[metadata_condition["R.Condition"]==run].index.values[0]
                concentrationlist.append([metadata_condition["Concentration"][fileindex]]*len(searchoutput.set_index("R.Condition").loc[run]))
            if "Concentration" in searchoutput.columns:
                searchoutput["Concentration"]=list(itertools.chain(*concentrationlist))
                searchoutput["Concentration"]=searchoutput["Concentration"].astype(int)
            else:
                searchoutput.insert(3,"Concentration",list(itertools.chain(*concentrationlist)))
                searchoutput["Concentration"]=searchoutput["Concentration"].astype(int)

        return searchoutput

#endregion

# ============================================================================= Generate Necessary Variables and Dataframes, Calculate Metrics
#region

    #take searchoutput df and generate variables and dataframes to be used downstream
    @reactive.calc
    def variables_dfs():
        searchoutput=metadata_update()
        searchoutput["R.Condition"]=searchoutput["R.Condition"].apply(str)
        if "Cond_Rep" not in searchoutput.columns:
            searchoutput.insert(0,"Cond_Rep",searchoutput["R.Condition"]+"_"+searchoutput["R.Replicate"].apply(str))
        elif "Cond_Rep" in searchoutput.columns:
            searchoutput["Cond_Rep"]=searchoutput["R.Condition"]+"_"+searchoutput["R.Replicate"].apply(str)
        resultdf=pd.DataFrame(searchoutput[["Cond_Rep","R.FileName","R.Condition","R.Replicate"]].drop_duplicates()).reset_index(drop=True)
        sampleconditions=searchoutput["R.Condition"].drop_duplicates().tolist()
        maxreplicatelist=[]
        for i in sampleconditions:
            samplegroup=pd.DataFrame(searchoutput[searchoutput["R.Condition"]==i])
            maxreplicates=max(samplegroup["R.Replicate"].tolist())
            maxreplicatelist.append(maxreplicates)
        averagedf=pd.DataFrame({"R.Condition":sampleconditions,"N.Replicates":maxreplicatelist})
        numconditions=len(averagedf["R.Condition"].tolist())
        repspercondition=averagedf["N.Replicates"].tolist()
        numsamples=len(resultdf["R.Condition"].tolist())

        return searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples
   
    #use the variables_dfs function that imports the searchoutput df to calculate ID metrics
    @reactive.calc
    def idmetrics():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
        numproteins=[]
        numproteins2pepts=[]
        numpeptides=[]
        numprecursors=[]

        for i in searchoutput["Cond_Rep"].drop_duplicates().reset_index(drop=True):
            replicatedata=searchoutput[searchoutput["Cond_Rep"]==i]

            if replicatedata.empty:
                continue
            #identified proteins
            numproteins.append(replicatedata["PG.ProteinNames"].nunique())
            #identified proteins with 2 peptides
            numproteins2pepts.append(len(replicatedata[["PG.ProteinNames","EG.ModifiedPeptide"]].drop_duplicates().groupby("PG.ProteinNames").size().reset_index(name="peptides").query("peptides>1")))
            #identified peptides
            numpeptides.append(replicatedata["EG.ModifiedPeptide"].nunique())
            #identified precursors
            numprecursors.append(len(replicatedata[["EG.ModifiedPeptide","FG.Charge"]].drop_duplicates()))
        resultdf["proteins"]=numproteins
        resultdf["proteins2pepts"]=numproteins2pepts
        resultdf["peptides"]=numpeptides
        resultdf["precursors"]=numprecursors
        
        #avg and stdev values for IDs appended to averagedf dataframe, which holds lists of all the calculated values here
        columnlist=resultdf.columns.values.tolist()
        for i in columnlist:
            if i=="R.FileName" or i=="Cond_Rep" or i=="R.Condition" or i=="R.Replicate":
                continue
            avglist=[]
            stdevlist=[]
            for j in sampleconditions:
                samplecondition=resultdf[resultdf["R.Condition"]==j]
                avglist.append(round(np.average(samplecondition[i].to_numpy())))
                stdevlist.append(np.std(samplecondition[i].to_numpy()))
            averagedf[i+"_avg"]=avglist
            averagedf[i+"_stdev"]=stdevlist

        return resultdf,averagedf

    #CV calculation
    @reactive.calc
    def cvcalc():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()

        cvcalc_df=pd.DataFrame()
        cvcalc_df["R.Condition"]=sampleconditions

        #protein-level CVs
        proteincvlist=[]
        proteincvlist95=[]
        proteincvdict={}
        cvproteingroup=searchoutput[["R.Condition","R.Replicate","PG.ProteinGroups","PG.MS2Quantity"]].drop_duplicates().reset_index(drop=True)
        for x,condition in enumerate(sampleconditions):
            if maxreplicatelist[x]==1:
                emptylist=[]
                proteincvlist.append(emptylist)
                proteincvlist95.append(emptylist)
            else:
                df=pd.DataFrame(cvproteingroup[cvproteingroup["R.Condition"]==condition]).drop(columns=["R.Condition","R.Replicate"])
                mean=df.groupby("PG.ProteinGroups").mean().rename(columns={"PG.MS2Quantity":"Protein Mean"})
                std=df.groupby("PG.ProteinGroups").std().rename(columns={"PG.MS2Quantity":"Protein Std"})
                cvproteintable=pd.concat([mean,std],axis=1)
                cvproteintable.dropna(inplace=True)
                cvlist=(cvproteintable["Protein Std"]/cvproteintable["Protein Mean"]*100).tolist()
                proteincvdict[condition]=pd.DataFrame(cvlist,columns=["CV"])
                proteincvlist.append(cvlist)
                top95=np.percentile(cvlist,95)
                cvlist95=[]
                for i in cvlist:
                    if i <=top95:
                        cvlist95.append(i)
                proteincvlist95.append(cvlist95)
        cvcalc_df["Protein CVs"]=proteincvlist
        cvcalc_df["Protein 95% CVs"]=proteincvlist95

        #precursor-level CVs
        precursorcvlist=[]
        precursorcvlist95=[]
        precursorcvdict={}
        cvprecursorgroup=searchoutput[["R.Condition","R.Replicate","EG.ModifiedPeptide","FG.Charge","FG.MS2Quantity"]].drop_duplicates().reset_index(drop=True)
        for x,condition in enumerate(sampleconditions):
            if maxreplicatelist[x]==1:
                emptylist=[]
                precursorcvlist.append(emptylist)
                precursorcvlist95.append(emptylist)
            else:
                df=pd.DataFrame(cvprecursorgroup[cvprecursorgroup["R.Condition"]==condition]).drop(columns=["R.Condition","R.Replicate"])
                mean=df.groupby(["EG.ModifiedPeptide","FG.Charge"]).mean().rename(columns={"FG.MS2Quantity":"Precursor Mean"})
                std=df.groupby(["EG.ModifiedPeptide","FG.Charge"]).std().rename(columns={"FG.MS2Quantity":"Precursor Std"})
                cvprecursortable=pd.concat([mean,std],axis=1)
                cvprecursortable.dropna(inplace=True)
                cvlist=(cvprecursortable["Precursor Std"]/cvprecursortable["Precursor Mean"]*100).tolist()
                precursorcvdict[condition]=pd.DataFrame(cvlist,columns=["CV"])
                precursorcvlist.append(cvlist)
                top95=np.percentile(cvlist,95)
                cvlist95=[]
                for i in cvlist:
                    if i <=top95:
                        cvlist95.append(i)
                precursorcvlist95.append(cvlist95)
        cvcalc_df["Precursor CVs"]=precursorcvlist
        cvcalc_df["Precursor 95% CVs"]=precursorcvlist95

        #counts above CV cutoffs
        #protein CVs
        proteinscv20=[]
        proteinscv10=[]
        for x,condition in enumerate(sampleconditions):
            if maxreplicatelist[x]==1:
                emptylist=[]
                proteinscv20.append(emptylist)
                proteinscv10.append(emptylist)
            else:
                proteinscv20.append(proteincvdict[condition][proteincvdict[condition]["CV"]<20].shape[0])
                proteinscv10.append(proteincvdict[condition][proteincvdict[condition]["CV"]<10].shape[0])

        cvcalc_df["proteinsCV<20"]=proteinscv20
        cvcalc_df["proteinsCV<10"]=proteinscv10

        #precursor CVs
        precursorscv20=[]
        precursorscv10=[]
        for x,condition in enumerate(sampleconditions):
            if maxreplicatelist[x]==1:
                emptylist=[]
                precursorscv20.append(emptylist)
                precursorscv10.append(emptylist)
            else:
                precursorscv20.append(precursorcvdict[condition][precursorcvdict[condition]["CV"]<20].shape[0])
                precursorscv10.append(precursorcvdict[condition][precursorcvdict[condition]["CV"]<10].shape[0])
        cvcalc_df["precursorsCV<20"]=precursorscv20
        cvcalc_df["precursorsCV<10"]=precursorscv10

        return cvcalc_df

    #charge states
    @reactive.calc
    def chargestates():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()

        chargestatedf_condition=pd.DataFrame()
        chargestatedf_run=pd.DataFrame()

        chargestatelist=[]
        chargestategroup=searchoutput[["R.Condition","PEP.StrippedSequence","FG.Charge"]].drop_duplicates().reset_index(drop=True)
        for condition in sampleconditions:
            df=pd.DataFrame(chargestategroup[chargestategroup["R.Condition"]==condition].drop(columns=["R.Condition","PEP.StrippedSequence"]))
            chargestatelist.append(df["FG.Charge"].tolist())
        chargestatedf_condition["Sample Names"]=sampleconditions
        chargestatedf_condition["Charge States"]=chargestatelist

        chargestatelist=[]
        chargestategroup=searchoutput[["Cond_Rep","PEP.StrippedSequence","FG.Charge"]].drop_duplicates().reset_index(drop=True)
        for run in searchoutput["Cond_Rep"].drop_duplicates().reset_index(drop=True):
            df=pd.DataFrame(chargestategroup[chargestategroup["Cond_Rep"]==run].drop(columns=["Cond_Rep","PEP.StrippedSequence"]))
            chargestatelist.append(df["FG.Charge"].tolist())
        chargestatedf_run["Sample Names"]=searchoutput["Cond_Rep"].drop_duplicates().reset_index(drop=True)
        chargestatedf_run["Charge States"]=chargestatelist

        return chargestatedf_condition,chargestatedf_run

    #peptide lengths
    @reactive.calc
    def peptidelengths():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()

        peptidelengths_condition=pd.DataFrame()
        peptidelengths_run=pd.DataFrame()

        listoflengths=[]
        for condition in sampleconditions:
            placeholder=searchoutput[searchoutput["R.Condition"]==condition]["PEP.StrippedSequence"].drop_duplicates().reset_index(drop=True).tolist()
            lengths=[]
            for pep in placeholder:
                lengths.append(len(pep))
            listoflengths.append(lengths)
        peptidelengths_condition["Sample Names"]=sampleconditions
        peptidelengths_condition["Peptide Lengths"]=listoflengths

        listoflengths=[]
        for run in searchoutput["Cond_Rep"].drop_duplicates().reset_index(drop=True):
            placeholder=searchoutput[searchoutput["Cond_Rep"]==run]["PEP.StrippedSequence"].drop_duplicates().reset_index(drop=True).tolist()
            lengths=[]
            for pep in placeholder:
                lengths.append(len(pep))
            listoflengths.append(lengths)
        peptidelengths_run["Sample Names"]=searchoutput["Cond_Rep"].drop_duplicates().reset_index(drop=True)
        peptidelengths_run["Peptide Lengths"]=listoflengths

        return peptidelengths_condition,peptidelengths_run

    #peptides per protein
    @reactive.calc
    def pepsperprotein():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()

        pepsperprotein_condition=pd.DataFrame()
        pepsperprotein_run=pd.DataFrame()

        pepsperproteinlist=[]
        for condition in sampleconditions:
            df=searchoutput[searchoutput["R.Condition"]==condition][["PG.ProteinNames","EG.ModifiedPeptide"]].drop_duplicates().reset_index(drop=True)
            pepsperproteinlist.append(df.groupby(["PG.ProteinNames"]).size().tolist())
        pepsperprotein_condition["Sample Names"]=sampleconditions
        pepsperprotein_condition["Peptides per Protein"]=pepsperproteinlist

        pepsperproteinlist=[]
        for run in searchoutput["Cond_Rep"].drop_duplicates().reset_index(drop=True):
            df=searchoutput[searchoutput["Cond_Rep"]==run][["PG.ProteinNames","EG.ModifiedPeptide"]].drop_duplicates().reset_index(drop=True)
            pepsperproteinlist.append(df.groupby(["PG.ProteinNames"]).size().tolist())
        pepsperprotein_run["Sample Names"]=searchoutput["Cond_Rep"].drop_duplicates().reset_index(drop=True)
        pepsperprotein_run["Peptides per Protein"]=pepsperproteinlist

        return pepsperprotein_condition,pepsperprotein_run

#endregion

# =============================# Sidebar Tabs #================================
# ============================================================================= Settings
#region

    @render.text
    def matplotlibcolors_text():
        return ("Matplotlib Tableau Colors:")
    @render.text
    def csscolors_text():
        return ("CSS Colors:")
    #function for showing color options as plots
    def plot_colortable(colors, *, ncols=4, sort_colors=True):
        #from https://matplotlib.org/stable/gallery/color/named_colors.html

        cell_width = 212
        cell_height = 22
        swatch_width = 48
        margin = 12

        # Sort colors by hue, saturation, value and name.
        if sort_colors is True:
            names = sorted(
                colors, key=lambda c: tuple(mcolors.rgb_to_hsv(mcolors.to_rgb(c))))
        else:
            names = list(colors)

        n = len(names)
        nrows = math.ceil(n / ncols)

        width = cell_width * ncols + 2 * margin
        height = cell_height * nrows + 2 * margin
        dpi = 72

        fig, ax = plt.subplots(figsize=(width / dpi, height / dpi), dpi=dpi)
        fig.subplots_adjust(margin/width, margin/height,
                            (width-margin)/width, (height-margin)/height)
        ax.set_xlim(0, cell_width * ncols)
        ax.set_ylim(cell_height * (nrows-0.5), -cell_height/2.)
        ax.yaxis.set_visible(False)
        ax.xaxis.set_visible(False)
        ax.set_axis_off()

        for i, name in enumerate(names):
            row = i % nrows
            col = i // nrows
            y = row * cell_height

            swatch_start_x = cell_width * col
            text_pos_x = cell_width * col + swatch_width + 7

            ax.text(text_pos_x, y, name, fontsize=14,
                    horizontalalignment='left',
                    verticalalignment='center')

            ax.add_patch(
                Rectangle(xy=(swatch_start_x, y-9), width=swatch_width,
                        height=18, facecolor=colors[name], edgecolor='0.7')
            )

        return fig
    @render.plot(width=200,height=500)
    def matplotlibcolors():
        return plot_colortable(mcolors.TABLEAU_COLORS, ncols=1, sort_colors=False)
    @render.plot(width=800,height=800)
    def csscolors():
        return plot_colortable(mcolors.CSS4_COLORS)
    #render the color grids as images instead of plotting them explicitly
    @render.image
    def matplotcolors_image():
        cwd=os.getcwd()
        foldername="images"
        joined=[cwd,foldername]
        matplotcolors_imagefile="\\".join([cwd,"images","matplotlib_tabcolors.png"])        
        img: ImgData={"src":matplotcolors_imagefile}
        return img
    @render.image
    def csscolors_image():
        cwd=os.getcwd()
        foldername="images"
        joined=[cwd,foldername]
        csscolors_imagefile="\\".join([cwd,"images","css_colors.png"])        
        img: ImgData={"src":csscolors_imagefile}
        return img

    #color options for plotting 
    @reactive.calc
    def colorpicker():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
        if input.coloroptions()=="pickrainbow":
            if numconditions==2:
                rainbowlist=cm.gist_rainbow(np.linspace(0,1,6))
                plotcolors=[]
                for i in range(len(rainbowlist)):
                    plotcolors.append(sns.desaturate(rainbowlist[i],0.75))
                indices=[0,3]
                plotcolors=[plotcolors[x] for x in indices]
            elif numconditions==1:
                plotcolors=sns.desaturate(cm.gist_rainbow(np.random.random_sample()),0.75)
            else:
                samplelinspace=np.linspace(0,1,numconditions)
                rainbowlist=cm.gist_rainbow(samplelinspace)
                plotcolors=[]
                for i in range(len(rainbowlist)):
                    plotcolors.append(sns.desaturate(rainbowlist[i],0.75))
        elif input.coloroptions()=="pickmatplot":
            matplottabcolors=list(mcolors.TABLEAU_COLORS)
            plotcolors=[]
            if numconditions > len(matplottabcolors):
                dif=numconditions-len(matplottabcolors)
                plotcolors=matplottabcolors
                for i in range(dif):
                    plotcolors.append(matplottabcolors[i])
            elif numconditions==1:
                plotcolors=matplottabcolors[np.random.randint(low=0,high=len(list(mcolors.TABLEAU_COLORS)))]
            else:
                for i in range(numconditions):
                    plotcolors.append(matplottabcolors[i])
        elif input.coloroptions()=="custom":
            if numconditions==1:
                plotcolors=input.customcolors()
            else:
                plotcolors=list(input.customcolors().split("\n"))
        return plotcolors
    
    #loop to extend list for replicates, used in the place of calling colorpicker() to have replicates of the same condition plotted with the same color
    @reactive.calc
    def replicatecolors():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
        plotcolors=colorpicker()
        if numconditions==1 and len(maxreplicatelist)==1:
            return plotcolors
        else:
            replicateplotcolors=[]
            for i in range(numconditions):
                x=repspercondition[i]
                for ele in range(x):
                    replicateplotcolors.append(plotcolors[i])
            return replicateplotcolors

    @render.text
    def colornote():
        return "Note: replicates of the same condition will have the same color"
    @render.table()
    def customcolors_table1():
        try:
            searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
            conditioncolordf1=pd.DataFrame({"Run":sampleconditions})
            return conditioncolordf1
        except:
            conditioncolordf1=pd.DataFrame({"Run":[]})
            return conditioncolordf1

    #show the conditions and color options for each condition
    @render.table
    def conditioncolors():
        conditioncolors_table=pd.DataFrame({"Color per run":[]})
        return conditioncolors_table

    @render.ui
    def colorplot_height():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
        height=40*numconditions
        return ui.input_numeric("colorplot_height_input","Color per run height mod *no touchy >:(*",value=height)

    @reactive.effect
    def _():
        @render.plot(width=75,height=input.colorplot_height_input())
        def customcolors_plot():
            try:
                searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
                plotcolors=colorpicker()
                
                fig,ax=plt.subplots(nrows=len(sampleconditions))
                fig.set_tight_layout(True)
                for i in range(len(sampleconditions)):
                    if len(sampleconditions)==1:
                        rect=matplotlib.patches.Rectangle(xy=(0,0),width=0.5,height=0.5,facecolor=plotcolors)
                        ax.add_patch(rect)
                        ax.axis("off")
                        ax.set_ylim(bottom=0,top=0.5)
                        ax.set_xlim(left=0,right=0.5)
                    else:
                        rect=matplotlib.patches.Rectangle(xy=(0,0),width=0.5,height=0.5,facecolor=plotcolors[i])
                        ax[i].add_patch(rect)
                        ax[i].axis("off")
                        ax[i].set_ylim(bottom=0,top=0.5)
                        ax[i].set_xlim(left=0,right=0.5)
            except:
                pass

    #stats about the input file
    @render.table
    def filestats():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()

        variablenames=["# samples","# conditions","Conditions","Replicates per Condition"]
        variablecalls=[numsamples,numconditions,sampleconditions,repspercondition]

        filestatsdf=pd.DataFrame({"Property":variablenames,"Values":variablecalls})
        
        return filestatsdf

    #preview of searchoutput table
    @render.data_frame
    def filepreview():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
        return render.DataGrid(searchoutput,editable=False,width="100%")

    #column check
    @render.table
    def column_check():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
        columnnames=searchoutput.columns.tolist()
        expectedcolumns=["R.FileName","PG.ProteinGroups","PG.ProteinAccessions","PG.ProteinNames","PG.MS2Quantity",
                        "PG.Genes","EG.ModifiedPeptide","FG.Charge","EG.Qvalue","PG.Qvalue",
                        "FG.MS2Quantity","FG.MS2RawQuantity","EG.ApexRT","EG.RTPredicted","EG.Cscore","EG.IonMobility",
                        "R.Condition","R.Replicate","Concentration","EG.PeakWidth",
                        "PEP.StrippedSequence","PEP.IsProteotypic","EG.FWHM","EG.IsImputed","FG.PrecMz"]
        columnnames=searchoutput.columns.tolist()
        in_report=[]
        for i in expectedcolumns:
            if i in columnnames:
                in_report.append("TRUE")
            else:
                in_report.append("NA")
        columncheck_df=pd.DataFrame({"Expected Column":expectedcolumns,"in_report":in_report})
        columncheck_df["Needed?"]=["Yes","Yes","","Yes","Yes","","Yes","Yes","Yes","Yes","Yes","","Yes","","","Yes","Yes","Yes","Yes","","Yes","","","","Yes"]
        return columncheck_df
        
#endregion  

# ============================================================================= ID Counts
#region

    #plot ID metrics
    @reactive.effect
    def _():
        if input.idplotinput()=="all":
            @render.plot(width=input.idmetrics_width(),height=input.idmetrics_height())
            def idmetricsplot():
                resultdf,averagedf=idmetrics()
                idmetricscolor=replicatecolors()
                figsize=(15,10)
                titlefont=input.titlefont()
                axisfont=input.axisfont()
                labelfont=input.labelfont()
                y_padding=input.ypadding()

                fig,ax=plt.subplots(nrows=2,ncols=2,figsize=figsize,sharex=True)
                fig.set_tight_layout(True)
                ax1=ax[0,0]
                ax2=ax[0,1]
                ax3=ax[1,0]
                ax4=ax[1,1]

                resultdf.plot.bar(ax=ax1,x="Cond_Rep",y="proteins",legend=False,width=0.8,color=idmetricscolor,edgecolor="k",fontsize=axisfont)
                ax1.bar_label(ax1.containers[0],label_type="edge",rotation=90,padding=5,fontsize=labelfont)
                ax1.set_ylim(top=max(resultdf["proteins"].tolist())+y_padding*max(resultdf["proteins"].tolist()))
                ax1.set_title("Protein Groups",fontsize=titlefont)

                resultdf.plot.bar(ax=ax2,x="Cond_Rep",y="proteins2pepts",legend=False,width=0.8,color=idmetricscolor,edgecolor="k",fontsize=axisfont)
                ax2.bar_label(ax2.containers[0],label_type="edge",rotation=90,padding=5,fontsize=labelfont)
                ax2.set_ylim(top=max(resultdf["proteins2pepts"].tolist())+y_padding*max(resultdf["proteins2pepts"].tolist()))
                ax2.set_title("Protein Groups with >2 Peptides",fontsize=titlefont)

                resultdf.plot.bar(ax=ax3,x="Cond_Rep",y="peptides",legend=False,width=0.8,color=idmetricscolor,edgecolor="k",fontsize=axisfont)
                ax3.bar_label(ax3.containers[0],label_type="edge",rotation=90,padding=5,fontsize=labelfont)
                ax3.set_ylim(top=max(resultdf["peptides"].tolist())+(y_padding+0.1)*max(resultdf["peptides"].tolist()))
                ax3.set_title("Peptides",fontsize=titlefont)
                ax3.set_xlabel("Condition",fontsize=axisfont)
                ax3.set_ylabel("  ",fontsize=axisfont)

                resultdf.plot.bar(ax=ax4,x="Cond_Rep",y="precursors",legend=False,width=0.8,color=idmetricscolor,edgecolor="k",fontsize=axisfont)
                ax4.bar_label(ax4.containers[0],label_type="edge",rotation=90,padding=5,fontsize=labelfont)
                ax4.set_ylim(top=max(resultdf["precursors"].tolist())+(y_padding+0.1)*max(resultdf["precursors"].tolist()))
                ax4.set_title("Precursors",fontsize=titlefont)
                ax4.set_xlabel("Condition",fontsize=axisfont)

                fig.text(0, 0.6,"Counts",ha="left",va="center",rotation="vertical",fontsize=axisfont)

                ax1.set_axisbelow(True)
                ax1.grid(linestyle="--")
                ax2.set_axisbelow(True)
                ax2.grid(linestyle="--")
                ax3.set_axisbelow(True)
                ax3.grid(linestyle="--")
                ax4.set_axisbelow(True)
                ax4.grid(linestyle="--")
        else:
            @render.plot(width=input.idmetrics_width(),height=input.idmetrics_height())
            def idmetricsplot():
                resultdf,averagedf=idmetrics()
                idmetricscolor=replicatecolors()
                plotinput=input.idplotinput()
                if plotinput=="proteins":
                    titleprop="Protein Groups"
                if plotinput=="proteins2pepts":
                    titleprop="Protein Groups with >2 Peptides"
                if plotinput=="peptides":
                    titleprop="Peptides"
                if plotinput=="precursors":
                    titleprop="Precursors"

                figsize=(15,10)
                titlefont=input.titlefont()
                axisfont=input.axisfont()
                labelfont=input.labelfont()
                y_padding=input.ypadding()

                fig,ax=plt.subplots()
                resultdf.plot.bar(ax=ax,x="Cond_Rep",y=plotinput,legend=False,width=0.8,color=idmetricscolor,edgecolor="k",fontsize=axisfont)
                ax.bar_label(ax.containers[0],label_type="edge",rotation=90,padding=5,fontsize=labelfont)
                ax.set_ylim(top=max(resultdf[plotinput].tolist())+y_padding*max(resultdf[plotinput].tolist()))
                ax.set_ylabel("Counts",fontsize=axisfont)
                ax.set_xlabel("Condition",fontsize=axisfont)
                ax.set_title(titleprop,fontsize=titlefont)
                ax.tick_params(axis="both",labelsize=axisfont)
                ax.set_axisbelow(True)
                ax.grid(linestyle="--")
    
    #plot average ID metrics
    @reactive.effect
    def _():
        if input.avgidplotinput()=="all":
            @render.plot(width=input.avgidmetrics_width(),height=input.avgidmetrics_height())
            def avgidmetricsplot():
                resultdf,averagedf=idmetrics()
                avgmetricscolor=colorpicker()

                figsize=(15,10)
                titlefont=input.titlefont()
                axisfont=input.axisfont()
                labelfont=input.labelfont()
                y_padding=input.ypadding()

                fig,ax=plt.subplots(nrows=2,ncols=2,figsize=figsize)
                fig.set_tight_layout(True)
                ax1=ax[0,0]
                ax2=ax[0,1]
                ax3=ax[1,0]
                ax4=ax[1,1]

                bars1=ax1.bar(averagedf["R.Condition"],averagedf["proteins_avg"],yerr=averagedf["proteins_stdev"],edgecolor="k",capsize=10,color=avgmetricscolor)
                ax1.bar_label(bars1,label_type="edge",rotation=90,padding=10,fontsize=labelfont)
                ax1.set_ylim(top=max(averagedf["proteins_avg"].tolist())+y_padding*max(averagedf["proteins_avg"].tolist()))
                ax1.set_title("Protein Groups",fontsize=titlefont)
                ax1.tick_params(axis='y',labelsize=axisfont)
                ax1.tick_params(axis='x',labelbottom=False)

                bars2=ax2.bar(averagedf["R.Condition"],averagedf["proteins2pepts_avg"],yerr=averagedf["proteins2pepts_stdev"],edgecolor="k",capsize=10,color=avgmetricscolor)
                ax2.bar_label(bars2,label_type="edge",rotation=90,padding=10,fontsize=labelfont)
                ax2.set_ylim(top=max(averagedf["proteins2pepts_avg"].tolist())+y_padding*max(averagedf["proteins2pepts_avg"].tolist()))
                ax2.set_title("Protein Groups with >2 Peptides",fontsize=titlefont)
                ax2.tick_params(axis='y',labelsize=axisfont)
                ax2.tick_params(axis='x',labelbottom=False)

                bars3=ax3.bar(averagedf["R.Condition"],averagedf["peptides_avg"],yerr=averagedf["peptides_stdev"],edgecolor="k",capsize=10,color=avgmetricscolor)
                ax3.bar_label(bars3,label_type="edge",rotation=90,padding=10,fontsize=labelfont)
                ax3.set_ylim(top=max(averagedf["peptides_avg"].tolist())+y_padding*max(averagedf["peptides_avg"].tolist()))
                ax3.set_title("Peptides",fontsize=titlefont)
                ax3.tick_params(axis='y',labelsize=axisfont)
                ax3.tick_params(axis='x',labelsize=axisfont,rotation=90)
                ax3.set_xlabel("Condition",fontsize=axisfont)
                ax3.set_ylabel("  ",fontsize=axisfont)

                bars4=ax4.bar(averagedf["R.Condition"],averagedf["precursors_avg"],yerr=averagedf["precursors_stdev"],edgecolor="k",capsize=10,color=avgmetricscolor)
                ax4.bar_label(bars4,label_type="edge",rotation=90,padding=10,fontsize=labelfont)
                ax4.set_ylim(top=max(averagedf["precursors_avg"].tolist())+y_padding*max(averagedf["precursors_avg"].tolist()))
                ax4.set_title("Precursors",fontsize=titlefont)
                ax4.tick_params(axis='y',labelsize=axisfont)
                ax4.tick_params(axis='x',labelsize=axisfont,rotation=90)
                ax4.set_xlabel("Condition",fontsize=axisfont)

                fig.text(0, 0.6,"Counts",ha="left",va="center",rotation="vertical",fontsize=axisfont)

                ax1.set_axisbelow(True)
                ax1.grid(linestyle="--")
                ax2.set_axisbelow(True)
                ax2.grid(linestyle="--")
                ax3.set_axisbelow(True)
                ax3.grid(linestyle="--")
                ax4.set_axisbelow(True)
                ax4.grid(linestyle="--")
            
        else:
            @render.plot(width=input.avgidmetrics_width(),height=input.avgidmetrics_height())
            def avgidmetricsplot():
                resultdf,averagedf=idmetrics()
                avgmetricscolor=colorpicker()
                avgplotinput=input.avgidplotinput()
                if avgplotinput=="proteins":
                    titleprop="Protein Groups"
                if avgplotinput=="proteins2pepts":
                    titleprop="Protein Groups with >2 Peptides"
                if avgplotinput=="peptides":
                    titleprop="Peptides"
                if avgplotinput=="precursors":
                    titleprop="Precursors"

                figsize=(15,10)
                titlefont=input.titlefont()
                axisfont=input.axisfont()
                labelfont=input.labelfont()
                y_padding=input.ypadding()
                fig,ax=plt.subplots()
                
                bars=ax.bar(averagedf["R.Condition"],averagedf[avgplotinput+"_avg"],yerr=averagedf[avgplotinput+"_stdev"],edgecolor="k",capsize=10,color=avgmetricscolor)
                ax.bar_label(bars,label_type="edge",rotation=90,padding=10,fontsize=labelfont)
                ax.set_ylim(top=max(averagedf[avgplotinput+"_avg"].tolist())+y_padding*max(averagedf[avgplotinput+"_avg"].tolist()))
                plt.ylabel("Counts",fontsize=axisfont)
                plt.xlabel("Condition",fontsize=axisfont)
                plt.title("Average #"+titleprop,fontsize=titlefont)
                ax.tick_params(axis="both",labelsize=axisfont)
                ax.tick_params(axis='x',labelsize=axisfont,rotation=90)
                ax.set_axisbelow(True)
                ax.grid(linestyle="--")

    #plot cv violin plots
    @reactive.effect
    def _():
        @render.plot(width=input.cvplot_width(),height=input.cvplot_height())
        def cvplot():
            cvcalc_df=cvcalc()

            violincolors=colorpicker()

            titlefont=input.titlefont()
            axisfont=input.axisfont()

            cvplotinput=input.proteins_precursors_cvplot()
            cutoff95=input.removetop5percent()

            x=np.arange(len(cvcalc_df["R.Condition"]))

            fig,ax=plt.subplots()

            medianlineprops=dict(linestyle="--",color="black")
            flierprops=dict(markersize=3)

            if cutoff95==True:
                bplot=ax.boxplot(cvcalc_df[cvplotinput+" 95% CVs"],medianprops=medianlineprops,flierprops=flierprops)
                plot=ax.violinplot(cvcalc_df[cvplotinput+" 95% CVs"],showextrema=False)#,showmeans=True)
                ax.set_title(cvplotinput+" CVs, 95% Cutoff",fontsize=titlefont)

            elif cutoff95==False:
                bplot=ax.boxplot(cvcalc_df[cvplotinput+" CVs"],medianprops=medianlineprops,flierprops=flierprops)
                plot=ax.violinplot(cvcalc_df[cvplotinput+" CVs"],showextrema=False)#,showmeans=True)
                ax.set_title(cvplotinput+" CVs",fontsize=titlefont)

            ax.set_xticks(x+1,labels=cvcalc_df["R.Condition"],fontsize=axisfont)
            ax.tick_params(axis="y",labelsize=axisfont)
            ax.set_ylabel("CV%",fontsize=axisfont)
            ax.set_xlabel("Condition",fontsize=axisfont)
            ax.grid(linestyle="--")
            ax.set_axisbelow(True)

            ax.axhline(y=20,color="black",linestyle="--")

            for z,color in zip(plot["bodies"],violincolors):
                z.set_facecolor(color)
                z.set_edgecolor("black")
                z.set_alpha(0.7)

    #plot counts with CV cutoffs
    @reactive.effect
    def _():
        @render.plot(width=input.countscvcutoff_width(),height=input.countscvcutoff_height())
        def countscvcutoff():
            resultdf,averagedf=idmetrics()

            cvcalc_df=cvcalc()

            titlefont=input.titlefont()
            axisfont=input.axisfont()
            labelfont=input.labelfont()
            legendfont=input.legendfont()
            y_padding=input.ypadding()

            x=np.arange(len(cvcalc_df["R.Condition"]))
            width=0.25

            cvinput=input.proteins_precursors_idcutoffplot()

            fig,ax=plt.subplots()

            ax.bar(x,averagedf[cvinput+"_avg"],width=width,label="Identified",edgecolor="k",color="#054169")
            ax.bar_label(ax.containers[0],label_type="edge",rotation=90,padding=5,fontsize=labelfont)

            ax.bar(x+width,cvcalc_df[cvinput+"CV<20"],width=width,label="CV<20%",edgecolor="k",color="#0071BC")
            ax.bar_label(ax.containers[1],label_type="edge",rotation=90,padding=5,fontsize=labelfont)

            ax.bar(x+(2*width),cvcalc_df[cvinput+"CV<10"],width=width,label="CV<10%",edgecolor="k",color="#737373")
            ax.bar_label(ax.containers[2],label_type="edge",rotation=90,padding=5,fontsize=labelfont)

            ax.set_ylim(top=max(averagedf[cvinput+"_avg"])+y_padding*max(averagedf[cvinput+"_avg"]))
            #ax.legend(ncols=3,loc="upper left",fontsize=axisfont)
            ax.legend(loc='center left', bbox_to_anchor=(1, 0.5),prop={'size':legendfont})
            ax.set_xticks(x+width,cvcalc_df["R.Condition"],fontsize=axisfont,rotation=90)
            ax.tick_params(axis="y",labelsize=axisfont)
            ax.set_xlabel("Condition",fontsize=axisfont)
            ax.set_ylabel("Counts",fontsize=axisfont)
            if cvinput=="proteins":
                ax.set_title("Protein Counts with CV Cutoffs",fontsize=titlefont)
            if cvinput=="precursors":
                ax.set_title("Precursor Counts with CV Cutoffs",fontsize=titlefont)
            ax.set_axisbelow(True)
            ax.grid(linestyle="--")

    #plot upset plot
    @reactive.effect
    def _():
        @render.plot(width=input.upsetplot_width(),height=input.upsetplot_height())
        def upsetplot():
            searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
            if input.protein_precursor_pick()=="Protein":
                proteindict=dict()
                for condition in sampleconditions:
                    proteinlist=searchoutput[searchoutput["R.Condition"]==condition][["R.Condition","PG.ProteinNames"]].drop_duplicates().reset_index(drop=True).drop(columns=["R.Condition"])
                    proteinlist.rename(columns={"PG.ProteinNames":condition},inplace=True)
                    proteindict[condition]=proteinlist[condition].tolist()
                proteins=from_contents(proteindict)

                fig=plt.figure()
                upset=UpSet(proteins,show_counts=True,sort_by="cardinality").plot(fig)
                upset["totals"].set_title("# Proteins")
                plt.ylabel("Protein Intersections",fontsize=14)
            elif input.protein_precursor_pick()=="Peptide":
                peptidedict=dict()
                for condition in sampleconditions:
                    peptidelist=searchoutput[searchoutput["R.Condition"]==condition][["R.Condition","EG.ModifiedPeptide"]].drop_duplicates().reset_index(drop=True).drop(columns=["R.Condition"])
                    peptidelist.rename(columns={"EG.ModifiedPeptide":condition},inplace=True)
                    peptidedict[condition]=peptidelist[condition].tolist()
                peptides=from_contents(peptidedict)
                fig=plt.figure()
                upset=UpSet(peptides,show_counts=True,sort_by="cardinality").plot(fig)
                upset["totals"].set_title("# Peptides")
                plt.ylabel("Peptide Intersections",fontsize=14)
            return fig
    
#endregion

# ============================================================================= Metrics
#region

    #plot charge states
    @reactive.effect
    def _():
        @render.plot(width=input.chargestate_width(),height=input.chargestate_height())
        def chargestateplot():
            
            figsize=(12,5)
            titlefont=input.titlefont()
            axisfont=input.axisfont()
            labelfont=input.labelfont()
            y_padding=0.15
        
            chargestatedf_condition,chargestatedf_run=chargestates()

            if input.chargestate_condition_or_run()=="condition":
                plottingdf=chargestatedf_condition
                chargestatecolor=colorpicker()
            if input.chargestate_condition_or_run()=="individual":
                plottingdf=chargestatedf_run
                chargestatecolor=replicatecolors()

            if len(plottingdf)==1:
                fig,ax=plt.subplots(figsize=(5,5))
                x=list(set(plottingdf["Charge States"][0]))
                frequencies=[len(list(group)) for key, group in groupby(sorted(plottingdf["Charge States"][0]))]
                
                totals=sum(frequencies)
                for y,ele in enumerate(frequencies):
                    frequencies[y]=round((ele/totals)*100,1)
                ax.bar(x,frequencies,edgecolor="k",color=chargestatecolor)
                ax.set_title(plottingdf["Sample Names"][0],fontsize=titlefont)
                ax.set_axisbelow(True)
                ax.grid(linestyle="--")
                ax.bar_label(ax.containers[0],label_type="edge",padding=10,fontsize=labelfont)

                ax.set_ylim(bottom=-5,top=max(frequencies)+y_padding*max(frequencies))
                ax.tick_params(axis="both",labelsize=axisfont)
                ax.set_xticks(np.arange(1,max(x)+1,1))
                ax.set_xlabel("Charge State",fontsize=axisfont)             
                ax.set_ylabel("Frequency (%)",fontsize=axisfont)
            else:
                fig,ax=plt.subplots(nrows=1,ncols=len(plottingdf),figsize=figsize)
                for i in range(len(plottingdf)):
                    x=list(set(plottingdf["Charge States"][i]))
                    frequencies=[len(list(group)) for key, group in groupby(sorted(plottingdf["Charge States"][i]))]

                    totals=sum(frequencies)
                    for y,ele in enumerate(frequencies):
                        frequencies[y]=round((ele/totals)*100,1)
                    ax[i].bar(x,frequencies,color=chargestatecolor[i],edgecolor="k")
                    ax[i].set_title(plottingdf["Sample Names"][i],fontsize=titlefont)
                    ax[i].set_axisbelow(True)
                    ax[i].grid(linestyle="--")
                    ax[i].bar_label(ax[i].containers[0],label_type="edge",padding=10,fontsize=labelfont)

                    ax[i].set_ylim(bottom=-5,top=max(frequencies)+y_padding*max(frequencies))
                    ax[i].tick_params(axis="both",labelsize=axisfont)
                    ax[i].set_xticks(np.arange(1,max(x)+1,1))
                    ax[i].set_xlabel("Charge State",fontsize=axisfont)
                ax[0].set_ylabel("Frequency (%)",fontsize=axisfont)
            fig.set_tight_layout(True)

    #render ui call for dropdown for marking peptide lengths
    @render.ui
    def lengthmark_ui():
        if input.peplengthinput()=="barplot":
            minlength=7
            maxlength=30
            opts=[item for item in range(minlength,maxlength+1)]
            opts.insert(0,0)
            return ui.input_selectize("lengthmark_pick","Pick peptide length to mark on bar plot (use 0 for maximum)",choices=opts)

    #plot peptide legnths
    @reactive.effect
    def _():
        @render.plot(width=input.peptidelength_width(),height=input.peptidelength_height())
        def peptidelengthplot():
            searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
            resultdf,averagedf=idmetrics()
            colors=colorpicker()

            titlefont=input.titlefont()
            axisfont=input.axisfont()
            labelfont=input.labelfont()
            legendfont=input.legendfont()
            y_padding=input.ypadding()

            peptidelengths_condition,peptidelengths_run=peptidelengths()

            if input.peptidelengths_condition_or_run()=="condition":
                plottingdf=peptidelengths_condition
                colors=colorpicker()
            if input.peptidelengths_condition_or_run()=="individual":
                plottingdf=peptidelengths_run
                colors=replicatecolors()

            if input.peplengthinput()=="lineplot":
                legendlist=[]
                fig,ax=plt.subplots(figsize=(6,4))
                for i in range(len(plottingdf)):
                    if len(plottingdf)==1:
                        x=list(set(plottingdf["Peptide Lengths"][0]))
                        frequencies=[len(list(group)) for key, group in groupby(sorted(plottingdf["Peptide Lengths"][0]))]
                        ax.plot(x,frequencies,color=colors,linewidth=2)
                        legendlist.append(plottingdf["Sample Names"][0])
                    else:
                        x=list(set(plottingdf["Peptide Lengths"][i]))
                        frequencies=[len(list(group)) for key, group in groupby(sorted(plottingdf["Peptide Lengths"][i]))]
                        ax.plot(x,frequencies,color=colors[i],linewidth=2)
                        legendlist.append(plottingdf["Sample Names"][i])
                ax.tick_params(axis="both",labelsize=axisfont)
                ax.set_xlabel("Peptide Length",fontsize=axisfont)
                ax.set_ylabel("Counts",fontsize=axisfont)
                ax.set_axisbelow(True)
                ax.grid(linestyle="--")
                ax.legend(legendlist,fontsize=legendfont)
                ax.xaxis.set_major_locator(MaxNLocator(integer=True))

            if input.peplengthinput()=="barplot":
                lengthmark=int(input.lengthmark_pick())
                if len(plottingdf)==1:
                    fig,ax=plt.subplots(figsize=(5,5))
                    x=list(set(plottingdf["Peptide Lengths"][0]))
                    frequencies=[len(list(group)) for key, group in groupby(sorted(plottingdf["Peptide Lengths"][0]))]
                    ax.bar(x,frequencies,color=colors,edgecolor="k")
                    ax.set_title(plottingdf["Sample Names"][0],fontsize=titlefont)
                    ax.set_axisbelow(True)
                    ax.grid(linestyle="--")
                    if lengthmark!=0:
                        ax.vlines(x=x[lengthmark-min(x)],ymin=frequencies[lengthmark-min(x)],ymax=frequencies[lengthmark-min(x)]+0.2*frequencies[lengthmark-min(x)],color="k")
                        ax.text(x=x[lengthmark-min(x)],y=frequencies[lengthmark-min(x)]+0.2*frequencies[lengthmark-min(x)],s=str(x[lengthmark-min(x)])+", "+str(frequencies[lengthmark-min(x)]),fontsize=labelfont)
                    elif lengthmark==0:
                        ax.vlines(x=x[np.argmax(frequencies)],ymin=max(frequencies),ymax=max(frequencies)+0.2*max(frequencies),color="k")
                        ax.text(x=x[np.argmax(frequencies)],y=max(frequencies)+0.2*max(frequencies),s=str(x[np.argmax(frequencies)])+", "+str(max(frequencies)),fontsize=labelfont)
                    ax.set_ylim(top=max(frequencies)+y_padding*max(frequencies))
                    ax.tick_params(axis="both",labelsize=axisfont)
                    ax.set_xlabel("Peptide Length",fontsize=axisfont)
                    ax.set_ylabel("Counts",fontsize=axisfont)
                else:
                    fig,ax=plt.subplots(nrows=1,ncols=len(plottingdf),figsize=(15,5))
                    for i in range(len(plottingdf)):
                        x=list(set(plottingdf["Peptide Lengths"][i]))
                        frequencies=[len(list(group)) for key, group in groupby(sorted(plottingdf["Peptide Lengths"][i]))]
                        ax[i].bar(x,frequencies,color=colors[i],edgecolor="k")
                        ax[i].set_title(plottingdf["Sample Names"][i],fontsize=titlefont)
                        ax[i].set_axisbelow(True)
                        ax[i].grid(linestyle="--")
                        if lengthmark!=0:
                            ax[i].vlines(x=x[lengthmark-min(x)],ymin=frequencies[lengthmark-min(x)],ymax=frequencies[lengthmark-min(x)]+0.2*frequencies[lengthmark-min(x)],color="k")
                            ax[i].text(x=x[lengthmark-min(x)],y=frequencies[lengthmark-min(x)]+0.2*frequencies[lengthmark-min(x)],s=str(x[lengthmark-min(x)])+", "+str(frequencies[lengthmark-min(x)]),fontsize=labelfont)
                        elif lengthmark==0:
                            ax[i].vlines(x=x[np.argmax(frequencies)],ymin=max(frequencies),ymax=max(frequencies)+0.2*max(frequencies),color="k")
                            ax[i].text(x=x[np.argmax(frequencies)],y=max(frequencies)+0.2*max(frequencies),s=str(x[np.argmax(frequencies)])+", "+str(max(frequencies)),fontsize=labelfont)
                        ax[i].set_ylim(top=max(frequencies)+y_padding*max(frequencies))
                        ax[i].tick_params(axis="both",labelsize=axisfont)
                        ax[i].set_xlabel("Peptide Length",fontsize=axisfont)
                    ax[0].set_ylabel("Counts",fontsize=axisfont)
            fig.set_tight_layout(True)
    
    #plot peptides per protein
    @reactive.effect
    def _():
        @render.plot(width=input.pepsperprotein_width(),height=input.pepsperprotein_height())
        def pepsperproteinplot():

            titlefont=input.titlefont()
            axisfont=input.axisfont()
            labelfont=input.labelfont()
            legendfont=input.legendfont()

            pepsperprotein_condition,pepsperprotein_run=pepsperprotein()

            if input.pepsperprotein_condition_or_run()=="condition":
                plottingdf=pepsperprotein_condition
                colors=colorpicker()
            if input.pepsperprotein_condition_or_run()=="individual":
                plottingdf=pepsperprotein_run
                colors=replicatecolors()

            if input.pepsperproteininput()=="lineplot":
                legendlist=[]
                fig,ax=plt.subplots(figsize=(6,4))

                if len(plottingdf)==1:
                    x=sorted(list(set(plottingdf["Peptides per Protein"][0])))
                    frequencies=[len(list(group)) for key, group in groupby(sorted(plottingdf["Peptides per Protein"][0]))]
                    ax.plot(x,frequencies,color=colors,linewidth=2)
                    legendlist.append(plottingdf["Sample Names"][0])
                else:
                    for i in range(len(plottingdf)):
                        x=sorted(list(set(plottingdf["Peptides per Protein"][i])))
                        frequencies=[len(list(group)) for key, group in groupby(sorted(plottingdf["Peptides per Protein"][i]))]
                        ax.plot(x,frequencies,color=colors[i],linewidth=2)
                        legendlist.append(plottingdf["Sample Names"][i])

                if max(x)>=100:
                    ax.set_xlim(left=0,right=100)
                ax.set_xlim(left=0)
                ax.tick_params(axis="both",labelsize=axisfont)
                ax.set_xlabel("Peptides per Protein",fontsize=axisfont)
                ax.set_ylabel("Counts",fontsize=axisfont)
                ax.set_axisbelow(True)
                ax.grid(linestyle="--")
                ax.legend(legendlist,fontsize=legendfont)

            if input.pepsperproteininput()=="barplot":
                if len(plottingdf)==1:
                    fig,ax=plt.subplots(figsize=(5,5))
                    for i in range(len(plottingdf)):
                        x=sorted(list(set(plottingdf["Peptides per Protein"][0])))
                        frequencies=[len(list(group)) for key, group in groupby(sorted(plottingdf["Peptides per Protein"][0]))]

                        ax.bar(x,frequencies,color=colors,width=0.025)
                        ax.set_title(plottingdf["Sample Names"][0],fontsize=titlefont)
                        ax.set_axisbelow(True)
                        ax.grid(linestyle="--")

                        ax.tick_params(axis="both",labelsize=axisfont)
                        ax.set_xticks(np.arange(0,max(x)+1,25))
                        ax.set_xlabel("# Peptides",fontsize=axisfont)
                        ax.set_ylabel("Counts",fontsize=axisfont)
                    if max(x)>=100:
                        ax.set_xlim(left=0,right=100)
                else:
                    fig,ax=plt.subplots(nrows=1,ncols=len(plottingdf),figsize=(15,5))
                    for i in range(len(plottingdf)):
                        x=list(set(plottingdf["Peptides per Protein"][i]))
                        frequencies=[len(list(group)) for key, group in groupby(sorted(plottingdf["Peptides per Protein"][i]))]

                        ax[i].bar(x,frequencies,color=colors[i])
                        ax[i].set_title(plottingdf["Sample Names"][i],fontsize=titlefont)
                        ax[i].set_axisbelow(True)
                        ax[i].grid(linestyle="--")

                        ax[i].tick_params(axis="both",labelsize=axisfont)
                        ax[i].set_xticks(np.arange(0,max(x)+1,25))
                        ax[i].set_xlabel("# Peptides",fontsize=axisfont)
                        if max(x)>=100:
                            ax[i].set_xlim(left=0,right=100)
                    ax[0].set_ylabel("Counts",fontsize=axisfont)
                fig.set_tight_layout(True)
    
    #plot dynamic range
    @render.plot(width=500,height=700)
    def dynamicrangeplot():
        conditioninput=input.conditionname()
        propertyinput=input.meanmedian()
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()

        markersize=25
        titlefont=input.titlefont()

        if propertyinput=="mean":
            intensitydf=searchoutput[searchoutput["R.Condition"]==conditioninput][["PG.ProteinNames","PG.MS2Quantity"]].drop_duplicates().groupby("PG.ProteinNames").mean().reset_index(drop=True)

        elif propertyinput=="median":
            intensitydf=searchoutput[searchoutput["R.Condition"]==conditioninput][["PG.ProteinNames","PG.MS2Quantity"]].drop_duplicates().groupby("PG.ProteinNames").median().reset_index(drop=True)

        fig,ax=plt.subplots(nrows=2,ncols=1,figsize=(5,7),sharex=True,gridspec_kw={"height_ratios":[1,3]})
        ax1=ax[0]
        ax2=ax[1]

        maxintensity=intensitydf.max()
        relative_fraction=(1-(intensitydf/maxintensity)).sort_values(by="PG.MS2Quantity").reset_index(drop=True)
        n_25=relative_fraction[relative_fraction["PG.MS2Quantity"]<0.25].shape[0]
        n_50=relative_fraction[relative_fraction["PG.MS2Quantity"]<0.50].shape[0]
        n_75=relative_fraction[relative_fraction["PG.MS2Quantity"]<0.75].shape[0]

        ax1.scatter(relative_fraction.index,relative_fraction["PG.MS2Quantity"],marker=".",s=markersize)
        ax1.set_ylabel("Relative Fraction")
        ax1.text(0,0.2,"- - - - - - - "+str(n_25)+" Protein groups")
        ax1.text(0,0.45,"- - - - - - - "+str(n_50)+" Protein groups")
        ax1.text(0,0.7,"- - - - - - - "+str(n_75)+" Protein groups")

        log10df=np.log10(intensitydf).sort_values(by="PG.MS2Quantity",ascending=False).reset_index(drop=True)
        dynamicrange=round(max(log10df["PG.MS2Quantity"])-min(log10df["PG.MS2Quantity"]),1)
        ax2.scatter(log10df.index,log10df["PG.MS2Quantity"],marker=".",s=markersize)
        ax2.set_ylabel("Log10(Area)")
        ax2.text(max(log10df.index)-0.6*(max(log10df.index)),max(log10df["PG.MS2Quantity"])-0.15*(max(log10df["PG.MS2Quantity"])),str(dynamicrange)+" log",fontsize=titlefont)

        plt.xlabel("Rank")
        plt.suptitle(conditioninput+" ("+propertyinput+"_PG)",x=0.13,horizontalalignment="left")
        ax1.set_axisbelow(True)
        ax2.set_axisbelow(True)
        ax1.grid(linestyle="--")
        ax2.grid(linestyle="--")
        fig.set_tight_layout(True)

    #get ranked proteins based on signal
    @render.data_frame
    def dynamicrange_proteinrank():
        conditioninput=input.conditionname()
        propertyinput=input.meanmedian()

        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()

        if propertyinput=="mean":
            intensitydf=searchoutput[searchoutput["R.Condition"]==conditioninput][["PG.ProteinNames","PG.MS2Quantity"]].drop_duplicates().groupby("PG.ProteinNames").mean().reset_index()
        elif propertyinput=="median":
            intensitydf=searchoutput[searchoutput["R.Condition"]==conditioninput][["PG.ProteinNames","PG.MS2Quantity"]].drop_duplicates().groupby("PG.ProteinNames").median().reset_index()
        intensitydf=intensitydf.sort_values("PG.MS2Quantity",ascending=False).reset_index(drop=True)

        return render.DataGrid(intensitydf.iloc[:input.top_n()],editable=False)

    #plot data completeness
    @reactive.effect
    def _():
        @render.plot(width=input.datacompleteness_width(),height=input.datacompleteness_height())
        def datacompletenessplot():
            searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()

            figsize=(12,5)
            titlefont=input.titlefont()
            axisfont=input.axisfont()
            labelfont=input.labelfont()
            y_padding=input.ypadding()
            labelpadding=1

            color1="tab:blue"
            color2="black"
            if input.protein_peptide()=="proteins":
                proteincounts=[len(list(group)) for key, group in groupby(sorted(searchoutput[["R.Condition","R.Replicate","PG.ProteinGroups"]].drop_duplicates().drop(columns=["R.Condition","R.Replicate"]).reset_index(drop=True).groupby(["PG.ProteinGroups"]).size().tolist()))]

            elif input.protein_peptide()=="peptides":
                proteincounts=[len(list(group)) for key, group in groupby(sorted(searchoutput[["R.Condition","R.Replicate","PEP.StrippedSequence"]].drop_duplicates().drop(columns=["R.Condition","R.Replicate"]).reset_index(drop=True).groupby(["PEP.StrippedSequence"]).size().tolist()))]

            totalproteins=sum(proteincounts)

            proteinfrequencies=[]
            for i in proteincounts:
                proteinfrequencies.append(i/totalproteins*100)

            xaxis=np.arange(1,len(proteinfrequencies)+1,1).tolist()

            y1=proteincounts
            y2=proteinfrequencies

            fig,ax1=plt.subplots(figsize=figsize)

            ax2 = ax1.twinx()
            ax1.bar(xaxis,y1,edgecolor="k")
            ax2.plot(xaxis,y2,"-o",color=color2)

            ax1.set_xlabel('Observed in X Runs',fontsize=axisfont)
            if input.protein_peptide()=="proteins":
                ax1.set_ylabel('# Proteins',color=color1,fontsize=axisfont)
            elif input.protein_peptide()=="peptides":
                ax1.set_ylabel('# Peptides',color=color1,fontsize=axisfont)
            ax2.set_ylabel('% of MS Runs',color=color2,fontsize=axisfont)
            ax1.tick_params(axis="x",labelsize=axisfont)
            ax1.tick_params(axis="y",colors=color1,labelsize=axisfont)
            ax2.tick_params(axis="y",colors=color2,labelsize=axisfont)

            ax1.bar_label(ax1.containers[0],label_type="edge",padding=35,color=color1,fontsize=labelfont)
            ax1.set_ylim(top=max(proteincounts)+y_padding*max(proteincounts))
            ax2.set_ylim(top=max(proteinfrequencies)+y_padding*max(proteinfrequencies))

            for x,y in enumerate(proteinfrequencies):
                ax2.text(xaxis[x],proteinfrequencies[x]+labelpadding,str(round(y,1))+"%",
                horizontalalignment="center",verticalalignment="bottom",color=color2,fontsize=labelfont)

            ax1.set_axisbelow(True)
            ax1.grid(linestyle="--")
            plt.xticks(range(1,len(xaxis)+1))
            plt.xlim(0.5,len(xaxis)+1)

    #plot peak widths
    @reactive.effect
    def _():
        @render.plot(width=input.peakwidth_width(),height=input.peakwidth_height())
        def peakwidthplot():
            searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()

            violincolors=replicatecolors()
            titlefont=input.titlefont()
            axisfont=input.axisfont()

            fwhm_dict=[]
            for run in searchoutput["Cond_Rep"].drop_duplicates().tolist():
                fwhm_dict.append(searchoutput[searchoutput["Cond_Rep"]==run]["EG.PeakWidth"]*60)
            x=np.arange(len(searchoutput["Cond_Rep"].drop_duplicates().tolist()))
            fig,ax=plt.subplots()
            medianlineprops=dict(linestyle="--",color="black")
            flierprops=dict(markersize=3)
            plot=ax.violinplot(fwhm_dict,showextrema=False)
            bplot=ax.boxplot(fwhm_dict,medianprops=medianlineprops,flierprops=flierprops)
            ax.set_ylabel("Peak Width (s)",fontsize=axisfont)
            ax.set_xlabel("Run",fontsize=axisfont)
            ax.set_xticks(x+1,labels=searchoutput["Cond_Rep"].drop_duplicates().tolist())
            ax.grid(linestyle="--")
            ax.set_axisbelow(True)
            for z,color in zip(plot["bodies"],violincolors):
                z.set_facecolor(color)
                z.set_edgecolor("black")
                z.set_alpha(0.7)

#endregion

# ============================================================================= PTMs 
#region

    #function for finding the PTMs in the data
    @reactive.calc
    def find_ptms():
        searchoutput=metadata_update()
        peplist=searchoutput["EG.ModifiedPeptide"]
        ptmlist=[]
        for i in peplist:
            ptmlist.append(re.findall(r"[^[]*\[([^]]*)\]",i))
        searchoutput["PTMs"]=ptmlist
        return(list(OrderedDict.fromkeys(itertools.chain(*ptmlist))))
    
    #function for doing ID calculations for a picked PTM
    #ptmresultdf,ptm=ptmcounts()
    @reactive.calc
    def ptmcounts():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
        resultdf,averagedf=idmetrics()
        ptm=input.foundptms()

        numptmproteins=[]
        numptmproteins2pepts=[]
        numptmpeptides=[]
        numptmprecursors=[]
        for condition in sampleconditions:
            for j in range(max(maxreplicatelist)+1):
                df=searchoutput[(searchoutput["R.Condition"]==condition)&(searchoutput["R.Replicate"]==j)][["R.Condition","R.Replicate","PG.ProteinNames","EG.ModifiedPeptide","FG.Charge"]]
                if df.empty:
                    continue
                #number of proteins with specified PTM
                numptmproteins.append(df[df["EG.ModifiedPeptide"].str.contains(ptm)]["PG.ProteinNames"].nunique())

                #number of proteins with 2 peptides and specified PTM
                numptmproteins2pepts.append(len(df[df["EG.ModifiedPeptide"].str.contains(ptm)][["PG.ProteinNames","EG.ModifiedPeptide"]].drop_duplicates().groupby("PG.ProteinNames").size().reset_index(name="peptides").query("peptides>1")))

                #number of peptides with specified PTM
                numptmpeptides.append(df[df["EG.ModifiedPeptide"].str.contains(ptm)]["EG.ModifiedPeptide"].nunique())

                #number of precursors with specified PTM
                numptmprecursors.append(len(df[df["EG.ModifiedPeptide"].str.contains(ptm)][["EG.ModifiedPeptide","FG.Charge"]].drop_duplicates()))

        ptmresultdf=pd.DataFrame({"Cond_Rep":resultdf["Cond_Rep"],"proteins":numptmproteins,"proteins2pepts":numptmproteins2pepts,"peptides":numptmpeptides,"precursors":numptmprecursors})

        propcolumnlist=["proteins","proteins2pepts","peptides","precursors"]

        for column in propcolumnlist:
            exec(f'ptmresultdf["{column}_enrich%"]=round((ptmresultdf["{column}"]/resultdf["{column}"])*100,1)')
        return ptmresultdf,ptm

    #generate list to pull from to pick PTMs
    @render.ui
    def ptmlist_ui():
        listofptms=find_ptms()
        ptmshortened=[]
        for i in range(len(listofptms)):
            ptmshortened.append(re.sub(r'\(.*?\)',"",listofptms[i]))
        ptmdict={ptmshortened[i]: listofptms[i] for i in range(len(listofptms))}
        return ui.input_selectize("foundptms","Pick PTM to plot data for",choices=ptmdict,selected=listofptms[0])

    #plot PTM ID metrics
    @reactive.effect
    def _():
        plotinput=input.ptmidplotinput()
        if plotinput=="all":
            @render.plot(width=input.ptmidmetrics_width(),height=input.ptmidmetrics_height())
            def ptmidmetricsplot():
                #colorblocks,colors,matplottabcolors,tabcolorsblocks=colordfs()
                #idmetricscolor=tabcolorsblocks

                idmetricscolor=replicatecolors()

                figsize=(15,10)
                titlefont=input.titlefont()
                axisfont=input.axisfont()
                labelfont=input.labelfont()
                y_padding=input.ypadding()

                ptmresultdf,ptm=ptmcounts()

                fig,ax=plt.subplots(nrows=2,ncols=2,figsize=figsize,sharex=True)
                fig.set_tight_layout(True)
                ax1=ax[0,0]
                ax2=ax[0,1]
                ax3=ax[1,0]
                ax4=ax[1,1]

                ptmresultdf.plot.bar(ax=ax1,x="Cond_Rep",y="proteins",legend=False,width=0.8,color=idmetricscolor,edgecolor="k",fontsize=axisfont)
                ax1.bar_label(ax1.containers[0],label_type="edge",rotation=90,padding=5,fontsize=labelfont)
                ax1.set_ylim(top=max(ptmresultdf["proteins"].tolist())+y_padding*max(ptmresultdf["proteins"].tolist()))
                ax1.set_title("Protein Groups",fontsize=titlefont)

                ptmresultdf.plot.bar(ax=ax2,x="Cond_Rep",y="proteins2pepts",legend=False,width=0.8,color=idmetricscolor,edgecolor="k",fontsize=axisfont)
                ax2.bar_label(ax2.containers[0],label_type="edge",rotation=90,padding=5,fontsize=labelfont)
                ax2.set_ylim(top=max(ptmresultdf["proteins2pepts"].tolist())+y_padding*max(ptmresultdf["proteins2pepts"].tolist()))
                ax2.set_title("Protein Groups with >2 Peptides",fontsize=titlefont)

                ptmresultdf.plot.bar(ax=ax3,x="Cond_Rep",y="peptides",legend=False,width=0.8,color=idmetricscolor,edgecolor="k",fontsize=axisfont)
                ax3.bar_label(ax3.containers[0],label_type="edge",rotation=90,padding=5,fontsize=labelfont)
                ax3.set_ylim(top=max(ptmresultdf["peptides"].tolist())+(y_padding+0.1)*max(ptmresultdf["peptides"].tolist()))
                ax3.set_title("Peptides",fontsize=titlefont)
                ax3.set_xlabel("Condition",fontsize=axisfont)
                ax3.set_ylabel("  ",fontsize=axisfont)

                ptmresultdf.plot.bar(ax=ax4,x="Cond_Rep",y="precursors",legend=False,width=0.8,color=idmetricscolor,edgecolor="k",fontsize=axisfont)
                ax4.bar_label(ax4.containers[0],label_type="edge",rotation=90,padding=5,fontsize=labelfont)
                ax4.set_ylim(top=max(ptmresultdf["precursors"].tolist())+(y_padding+0.1)*max(ptmresultdf["precursors"].tolist()))
                ax4.set_title("Precursors",fontsize=titlefont)
                ax4.set_xlabel("Condition",fontsize=axisfont)

                fig.text(0, 0.6,"Counts",ha="left",va="center",rotation="vertical",fontsize=axisfont)

                ax1.set_axisbelow(True)
                ax1.grid(linestyle="--")
                ax2.set_axisbelow(True)
                ax2.grid(linestyle="--")
                ax3.set_axisbelow(True)
                ax3.grid(linestyle="--")
                ax4.set_axisbelow(True)
                ax4.grid(linestyle="--")
                plt.suptitle("ID Counts for PTM: "+ptm,y=1,fontsize=titlefont)
            
        else:
            @render.plot(width=input.ptmidmetrics_width(),height=input.ptmidmetrics_height())
            def ptmidmetricsplot():
                idmetricscolor=replicatecolors()

                if plotinput=="proteins":
                    titleprop="Proteins"
                if plotinput=="proteins2pepts":
                    titleprop="Proteins with >2 Peptides"
                if plotinput=="peptides":
                    titleprop="Peptides"
                if plotinput=="precursors":
                    titleprop="Precursors"

                figsize=(15,10)
                titlefont=input.titlefont()
                axisfont=input.axisfont()
                labelfont=input.labelfont()
                y_padding=input.ypadding()

                ptmresultdf,ptm=ptmcounts()
                fig,ax=plt.subplots()
                ptmresultdf.plot.bar(ax=ax,x="Cond_Rep",y=plotinput,legend=False,width=0.8,color=idmetricscolor,edgecolor="k")
                ax.bar_label(ax.containers[0],label_type="edge",rotation=90,padding=5,fontsize=labelfont)
                ax.set_ylim(top=max(ptmresultdf[plotinput].tolist())+y_padding*max(ptmresultdf[plotinput].tolist()))
                plt.ylabel("Counts",fontsize=axisfont)
                plt.xlabel("Condition",fontsize=axisfont)
                plt.title(titleprop,fontsize=titlefont)
                ax.tick_params(axis="both",labelsize=axisfont)
                ax.set_axisbelow(True)
                ax.grid(linestyle="--")
                plt.suptitle("ID Counts for PTM: "+ptm,y=1,fontsize=titlefont)

    #plot PTM enrichment
    @reactive.effect
    def _():
        plotinput=input.ptmenrichplotinput()
        if plotinput=="all":
            @render.plot(width=input.ptmenrichment_width(),height=input.ptmenrichment_height())
            def ptmenrichment():
                #colorblocks,colors,matplottabcolors,tabcolorsblocks=colordfs()
                #idmetricscolor=tabcolorsblocks
                idmetricscolor=replicatecolors()
                figsize=(15,10)
                titlefont=input.titlefont()
                axisfont=input.axisfont()
                labelfont=input.labelfont()
                y_padding=input.ypadding()

                ptmresultdf,ptm=ptmcounts()

                fig,ax=plt.subplots(nrows=2,ncols=2,figsize=figsize,sharex=True)
                fig.set_tight_layout(True)
                ax1=ax[0,0]
                ax2=ax[0,1]
                ax3=ax[1,0]
                ax4=ax[1,1]

                ptmresultdf.plot.bar(ax=ax1,x="Cond_Rep",y="proteins_enrich%",legend=False,width=0.8,color=idmetricscolor,edgecolor="k",fontsize=axisfont)
                ax1.bar_label(ax1.containers[0],label_type="edge",rotation=90,padding=5,fontsize=labelfont)
                ax1.set_ylim(top=max(ptmresultdf["proteins_enrich%"].tolist())+y_padding*max(ptmresultdf["proteins_enrich%"].tolist()))
                ax1.set_title("Protein Groups",fontsize=titlefont)

                ptmresultdf.plot.bar(ax=ax2,x="Cond_Rep",y="proteins2pepts_enrich%",legend=False,width=0.8,color=idmetricscolor,edgecolor="k",fontsize=axisfont)
                ax2.bar_label(ax2.containers[0],label_type="edge",rotation=90,padding=5,fontsize=labelfont)
                ax2.set_ylim(top=max(ptmresultdf["proteins2pepts_enrich%"].tolist())+y_padding*max(ptmresultdf["proteins2pepts_enrich%"].tolist()))
                ax2.set_title("Protein Groups with >2 Peptides",fontsize=titlefont)

                ptmresultdf.plot.bar(ax=ax3,x="Cond_Rep",y="peptides_enrich%",legend=False,width=0.8,color=idmetricscolor,edgecolor="k",fontsize=axisfont)
                ax3.bar_label(ax3.containers[0],label_type="edge",rotation=90,padding=5,fontsize=labelfont)
                ax3.set_ylim(top=max(ptmresultdf["peptides_enrich%"].tolist())+y_padding*max(ptmresultdf["peptides_enrich%"].tolist()))
                ax3.set_title("Peptides",fontsize=titlefont)
                ax3.set_xlabel("Condition",fontsize=axisfont)
                ax3.set_ylabel("  ",fontsize=axisfont)

                ptmresultdf.plot.bar(ax=ax4,x="Cond_Rep",y="precursors_enrich%",legend=False,width=0.8,color=idmetricscolor,edgecolor="k",fontsize=axisfont)
                ax4.bar_label(ax4.containers[0],label_type="edge",rotation=90,padding=5,fontsize=labelfont)
                ax4.set_ylim(top=max(ptmresultdf["precursors_enrich%"].tolist())+y_padding*max(ptmresultdf["precursors_enrich%"].tolist()))
                ax4.set_title("Precursors",fontsize=titlefont)
                ax4.set_xlabel("Condition",fontsize=axisfont)

                fig.text(0.01, 0.6,"Enrichment %",ha="center",va="center",rotation="vertical",fontsize=axisfont)

                ax1.set_axisbelow(True)
                ax1.grid(linestyle="--")
                ax2.set_axisbelow(True)
                ax2.grid(linestyle="--")
                ax3.set_axisbelow(True)
                ax3.grid(linestyle="--")
                ax4.set_axisbelow(True)
                ax4.grid(linestyle="--")
                plt.suptitle("Enrichment for PTM: "+ptm,y=1,fontsize=titlefont)
            
        else:
            @render.plot(width=input.ptmenrichment_width(),height=input.ptmenrichment_height())
            def ptmenrichment():
                idmetricscolor=replicatecolors()

                if plotinput=="proteins":
                    titleprop="Proteins"
                if plotinput=="proteins2pepts":
                    titleprop="Proteins with >2 Peptides"
                if plotinput=="peptides":
                    titleprop="Peptides"
                if plotinput=="precursors":
                    titleprop="Precursors"

                figsize=(15,10)
                titlefont=input.titlefont()
                axisfont=input.axisfont()
                labelfont=input.labelfont()
                y_padding=input.ypadding()

                ptmresultdf,ptm=ptmcounts()

                fig,ax=plt.subplots()
                ptmresultdf.plot.bar(ax=ax,x="Cond_Rep",y=str(plotinput+"_enrich%"),legend=False,width=0.8,color=idmetricscolor,edgecolor="k")
                ax.bar_label(ax.containers[0],label_type="edge",rotation=90,padding=5,fontsize=labelfont)
                ax.set_ylim(top=max(ptmresultdf[str(plotinput+"_enrich%")].tolist())+y_padding*max(ptmresultdf[str(plotinput+"_enrich%")].tolist()))
                plt.ylabel("Enrichment %",fontsize=axisfont)
                plt.xlabel("Condition",fontsize=axisfont)
                plt.title(str(titleprop+" Enrichment %"),fontsize=titlefont)
                ax.tick_params(axis="both",labelsize=axisfont)
                ax.set_axisbelow(True)
                ax.grid(linestyle="--")
                plt.suptitle("Enrichment for PTM: "+ptm,y=1,fontsize=titlefont)

    #plot PTM CV violin plots
    @reactive.effect
    def _():
        @render.plot(width=input.ptmcvplot_width(),height=input.ptmcvplot_height())
        def ptm_cvplot():
            #colorblocks,colors,matplottabcolors,tabcolorsblocks=colordfs()
            searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
            resultdf,averagedf=idmetrics()
            ptmresultdf,ptm=ptmcounts()
            colors=colorpicker()
            cvplotinput=input.ptm_proteins_precursors()
            cutoff95=input.ptm_removetop5percent()
            
            figsize=(15,10)
            titlefont=input.titlefont()
            axisfont=input.axisfont()

            ptmcvs=pd.DataFrame()
            ptmcvs["R.Condition"]=averagedf["R.Condition"]
            proteincv=[]
            proteinptmcv95=[]
            precursorcv=[]
            precursorptmcv95=[]

            df=searchoutput[["R.Condition","R.Replicate","PG.ProteinNames","PG.MS2Quantity","FG.Charge","EG.ModifiedPeptide","FG.MS2Quantity"]].drop_duplicates().reset_index(drop=True)
            for x,condition in enumerate(averagedf["R.Condition"]):
                ptmdf=df[df["R.Condition"]==condition][["R.Condition","R.Replicate","PG.ProteinNames","PG.MS2Quantity","FG.Charge","EG.ModifiedPeptide","FG.MS2Quantity"]].drop_duplicates().reset_index(drop=True)
                
                if maxreplicatelist[x]==1:
                    emptylist=[]
                    proteincv.append(emptylist)
                    proteinptmcv95.append(emptylist)
                    precursorcv.append(emptylist)
                    precursorptmcv95.append(emptylist)
                else:
                    #protein CVs for specified PTMs
                    mean=ptmdf[ptmdf["EG.ModifiedPeptide"].str.contains(ptm)!=False][["R.Condition","PG.ProteinNames","PG.MS2Quantity"]].drop_duplicates().groupby(["R.Condition","PG.ProteinNames"]).mean().rename(columns={"PG.MS2Quantity":"PTM Protein Mean"}).reset_index(drop=True)
                    stdev=ptmdf[ptmdf["EG.ModifiedPeptide"].str.contains(ptm)!=False][["R.Condition","PG.ProteinNames","PG.MS2Quantity"]].drop_duplicates().groupby(["R.Condition","PG.ProteinNames"]).std().rename(columns={"PG.MS2Quantity":"PTM Protein Stdev"}).reset_index(drop=True)
                    cvptmproteintable=pd.concat([mean,stdev],axis=1)
                    cvptmproteintable["PTM CV"]=(cvptmproteintable["PTM Protein Stdev"]/cvptmproteintable["PTM Protein Mean"]*100).tolist()
                    cvptmproteintable.drop(columns=["PTM Protein Mean","PTM Protein Stdev"],inplace=True)
                    cvptmproteintable.dropna(inplace=True)
                    proteincv.append(cvptmproteintable["PTM CV"].tolist())
                    top95=np.percentile(cvptmproteintable,95)
                    ptmcvlist95=[]
                    for i in cvptmproteintable["PTM CV"].tolist():
                        if i <=top95:
                            ptmcvlist95.append(i)
                    proteinptmcv95.append(ptmcvlist95)
                    
                    #precursor CVs for specified PTMs
                    mean=ptmdf[ptmdf["EG.ModifiedPeptide"].str.contains(ptm)!=False][["R.Condition","EG.ModifiedPeptide","FG.Charge","FG.MS2Quantity"]].groupby(["R.Condition","EG.ModifiedPeptide","FG.Charge"]).mean().rename(columns={"FG.MS2Quantity":"PTM Precursor Mean"}).reset_index(drop=True)
                    stdev=ptmdf[ptmdf["EG.ModifiedPeptide"].str.contains(ptm)!=False][["R.Condition","EG.ModifiedPeptide","FG.Charge","FG.MS2Quantity"]].groupby(["R.Condition","EG.ModifiedPeptide","FG.Charge"]).std().rename(columns={"FG.MS2Quantity":"PTM Precursor Stdev"}).reset_index(drop=True)
                    cvptmprecursortable=pd.concat([mean,stdev],axis=1)
                    cvptmprecursortable["PTM CV"]=(cvptmprecursortable["PTM Precursor Stdev"]/cvptmprecursortable["PTM Precursor Mean"]*100).tolist()
                    cvptmprecursortable.drop(columns=["PTM Precursor Mean","PTM Precursor Stdev"],inplace=True)
                    cvptmprecursortable.dropna(inplace=True)
                    precursorcv.append(cvptmprecursortable["PTM CV"].tolist())
                    top95=np.percentile(cvptmprecursortable,95)
                    ptmcvlist95=[]
                    for i in cvptmprecursortable["PTM CV"].tolist():
                        if i <=top95:
                            ptmcvlist95.append(i)
                    precursorptmcv95.append(ptmcvlist95)
            ptmcvs["Protein CVs"]=proteincv
            ptmcvs["Protein 95% CVs"]=proteinptmcv95
            ptmcvs["Precursor CVs"]=precursorcv
            ptmcvs["Precursor 95% CVs"]=precursorptmcv95

            n=len(sampleconditions)
            x=np.arange(n)

            fig,ax=plt.subplots(figsize=figsize)

            medianlineprops=dict(linestyle="--",color="black")
            flierprops=dict(markersize=3)

            if cutoff95==True:
                bplot=ax.boxplot(ptmcvs[cvplotinput+" 95% CVs"],medianprops=medianlineprops,flierprops=flierprops)
                plot=ax.violinplot(ptmcvs[cvplotinput+" 95% CVs"],showextrema=False)#,showmeans=True)
                ax.set_title(cvplotinput+" CVs for PTM: "+ptm+", 95% Cutoff",fontsize=titlefont)

            elif cutoff95==False:
                bplot=ax.boxplot(ptmcvs[cvplotinput+" CVs"],medianprops=medianlineprops,flierprops=flierprops)
                plot=ax.violinplot(ptmcvs[cvplotinput+" CVs"],showextrema=False)#,showmeans=True)
                ax.set_title(cvplotinput+" CVs for PTM: "+ptm,fontsize=titlefont)

            ax.set_xticks(x+1,labels=ptmcvs["R.Condition"],fontsize=axisfont)
            ax.tick_params(axis="y",labelsize=axisfont)
            ax.set_ylabel("CV%",fontsize=axisfont)
            ax.set_xlabel("Condition",fontsize=axisfont)
            ax.grid(linestyle="--")
            ax.set_axisbelow(True)

            ax.axhline(y=20,color="black",linestyle="--")

            for z,color in zip(plot["bodies"],colors):
                z.set_facecolor(color)
                z.set_edgecolor("black")
                z.set_alpha(0.7)

    #plot PTMs per precursor
    @reactive.effect
    def _():
        width=input.barwidth()
        @render.plot(width=input.ptmsperprecursor_width(),height=input.ptmsperprecursor_height())
        def ptmsperprecursor():
            searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
            resultdf,averagedf=idmetrics()

            colors=colorpicker()

            titlefont=input.titlefont()
            axisfont=input.axisfont()
            labelfont=input.labelfont()
            legendfont=input.legendfont()
            y_padding=input.ypadding()

            fig,ax=plt.subplots()
            ptmdf=pd.DataFrame()

            for j,condition in enumerate(sampleconditions):
                df=searchoutput[searchoutput["R.Condition"]==condition][["EG.ModifiedPeptide","FG.Charge"]].drop_duplicates().reset_index(drop=True)
                dfptmlist=[]
                numptms=[]
                for i in df["EG.ModifiedPeptide"]:
                    foundptms=re.findall(r"[^[]*\[([^]]*)\]",i)
                    dfptmlist.append(foundptms)
                    numptms.append(len(foundptms))
                dfptmlist=pd.Series(dfptmlist).value_counts().to_frame().reset_index().rename(columns={"index":condition,"count":condition+"_count"})
                ptmdf=pd.concat([ptmdf,dfptmlist],axis=1)
                
                x=np.arange(0,max(numptms)+1,1)
                frequencies=pd.Series(numptms).value_counts()
                if numconditions==1:
                    ax.bar(x+(j*width),frequencies,width=width,color=colors,edgecolor="black")
                else:
                    ax.bar(x+(j*width),frequencies,width=width,color=colors[j],edgecolor="black")
                ax.bar_label(ax.containers[j],label_type="edge",rotation=90,padding=5,fontsize=labelfont)

            ax.legend(sampleconditions,loc="upper right",fontsize=legendfont)
            ax.set_ylim(bottom=-1000,top=ax.get_ylim()[1]+y_padding*ax.get_ylim()[1])
            ax.set_xticks(x+((numconditions-1)/2)*width,x)
            ax.tick_params(axis="both",labelsize=axisfont)
            ax.set_ylabel("Counts",fontsize=axisfont)
            ax.set_xlabel("# of PTMs",fontsize=axisfont)
            ax.set_title("# of PTMs per Precursor",fontsize=titlefont)
            ax.set_axisbelow(True)
            ax.grid(linestyle="--")

            return fig

#endregion    

# ============================================================================= Heatmaps
#region

    @render.ui
    def cond_rep_list_heatmap():
        if input.conditiontype()=="replicate":
            searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
            opts=resultdf["Cond_Rep"].tolist()
            return ui.input_selectize("cond_rep_heatmap","Pick run to show:",choices=opts)               
        elif input.conditiontype()=="condition":
            searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
            opts=resultdf["R.Condition"].tolist()
            return ui.input_selectize("cond_rep_heatmap","Pick condition to show:",choices=opts)   

    #plot 2D heatmaps for RT, m/z, mobility
    @render.plot(width=1400,height=1000)
    def replicate_heatmap():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()

        titlefont=input.titlefont()
        axisfont=input.axisfont()
        labelfont=input.labelfont()
        figsize=(15,10)

        numbins=input.heatmap_numbins()

        conditioninput=input.cond_rep_heatmap()
        if input.conditiontype()=="replicate":
            his2dsample=searchoutput[searchoutput["Cond_Rep"]==conditioninput][["Cond_Rep","EG.IonMobility","EG.ApexRT","FG.PrecMz","FG.MS2Quantity"]].sort_values(by="EG.ApexRT").reset_index(drop=True)
        elif input.conditiontype()=="condition":
            his2dsample=searchoutput[searchoutput["R.Condition"]==conditioninput][["R.Condition","EG.IonMobility","EG.ApexRT","FG.PrecMz","FG.MS2Quantity"]].sort_values(by="EG.ApexRT").reset_index(drop=True)

        samplename=conditioninput
        cmap=matplotlib.colors.LinearSegmentedColormap.from_list("",["white","blue","red"])

        fig,ax=plt.subplots(nrows=2,ncols=2,figsize=figsize)

        i=ax[0,0].hist2d(his2dsample["EG.ApexRT"],his2dsample["FG.PrecMz"],bins=numbins,cmap=cmap)
        ax[0,0].set_title("RT vs m/z",fontsize=titlefont)
        ax[0,0].set_xlabel("Retention Time (min)",fontsize=axisfont)
        ax[0,0].set_ylabel("m/z",fontsize=axisfont)
        fig.colorbar(i[3],ax=ax[0,0])

        j=ax[0,1].hist2d(his2dsample["FG.PrecMz"],his2dsample["EG.IonMobility"],bins=numbins,cmap=cmap)
        ax[0,1].set_title("m/z vs Mobility",fontsize=titlefont)
        ax[0,1].set_xlabel("m/z",fontsize=axisfont)
        ax[0,1].set_ylabel("Ion Mobility ($1/K_{0}$)",fontsize=axisfont)
        fig.colorbar(j[3],ax=ax[0,1])

        ax[1,0].plot(his2dsample["EG.ApexRT"],his2dsample["FG.MS2Quantity"],color="blue",linewidth=0.5)
        ax[1,0].set_title("RT vs Intensity (line plot)",fontsize=titlefont)
        ax[1,0].set_xlabel("Retention Time (min)",fontsize=axisfont)
        ax[1,0].set_ylabel("Intensity",fontsize=axisfont)

        k=ax[1,1].hist2d(his2dsample["EG.ApexRT"].sort_values(),his2dsample["EG.IonMobility"],bins=numbins,cmap=cmap)
        ax[1,1].set_title("RT vs Mobility",fontsize=titlefont)
        ax[1,1].set_xlabel("Retention Time (min)",fontsize=axisfont)
        ax[1,1].set_ylabel("Ion Mobility ($1/K_{0}$)",fontsize=axisfont)
        fig.colorbar(k[3],ax=ax[1,1])
        fig.set_tight_layout(True)
        plt.suptitle("Histograms of Identified Precursors"+", "+samplename,y=1,fontsize=titlefont)

    #imported DIA windows
    def diawindows_import():
        if input.diawindow_upload() is None:
            return pd.DataFrame()
        diawindows=pd.read_csv(input.diawindow_upload()[0]["datapath"])
        diawindows=diawindows.drop(index=0).reset_index(drop=True)
        startcoords=[]
        for i in range(len(diawindows)):
            startcorner=float(diawindows["Start Mass [m/z]"][i]),float(diawindows["Start IM [1/K0]"][i])
            startcoords.append(startcorner)
        diawindows["W"]=diawindows["End Mass [m/z]"].astype(float)-diawindows["Start Mass [m/z]"].astype(float)
        diawindows["H"]=diawindows["End IM [1/K0]"].astype(float)-diawindows["Start IM [1/K0]"].astype(float)
        diawindows["xy"]=startcoords
        return diawindows
    #Lubeck DIA windows
    def lubeckdiawindow():
        lubeckdia=pd.DataFrame({
            "#MS Type":['PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF'],
            "Cycle Id":[1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5, 5, 6, 6, 6, 7, 7, 7, 8, 8, 8, 9, 9, 9, 10, 10, 10, 11, 11, 11, 12, 12, 12, 13, 13, 13, 14, 14, 14, 15, 15, 15, 16, 16, 16, 17, 17, 17, 18, 18, 18, 19, 19, 19, 20, 20, 20],
            "Start IM [1/K0]":[0.965, 0.805, 0.6, 0.977, 0.87, 0.6, 0.986, 0.89, 0.6, 0.995, 0.9, 0.6, 1.006, 0.906, 0.6, 1.025, 0.91, 0.6, 1.045, 0.917, 0.6, 1.064, 0.927, 0.6, 1.085, 0.94, 0.6, 1.105, 0.955, 0.6, 0.97, 0.85, 0.6, 0.982, 0.884, 0.6, 0.99, 0.895, 0.6, 1.0, 0.903, 0.6, 1.015, 0.908, 0.6, 1.034, 0.914, 0.6, 1.054, 0.92, 0.6, 1.075, 0.934, 0.6, 1.095, 0.947, 0.6, 1.11, 0.96, 0.6],
            "End IM [1/K0]":[1.12, 0.965, 0.805, 1.15, 0.977, 0.87, 1.19, 0.986, 0.89, 1.23, 0.995, 0.9, 1.27, 1.006, 0.906, 1.31, 1.025, 0.91, 1.35, 1.045, 0.917, 1.39, 1.064, 0.927, 1.43, 1.085, 0.94, 1.45, 1.105, 0.955, 1.13, 0.97, 0.85, 1.17, 0.982, 0.884, 1.21, 0.99, 0.895, 1.25, 1.0, 0.903, 1.29, 1.015, 0.908, 1.33, 1.034, 0.914, 1.37, 1.054, 0.92, 1.41, 1.075, 0.934, 1.44, 1.095, 0.947, 1.45, 1.11, 0.96],
            "Start Mass [m/z]":[725.13, 559.8, 350.68, 746.34, 574.21, 412.39, 769.41, 588.81, 437.42, 794.87, 603.8, 456.05, 821.43, 619.33, 472.76, 851.93, 635.35, 488.1, 886.49, 651.86, 502.77, 928.86, 668.83, 517.08, 982.67, 686.35, 531.29, 1059.54, 704.89, 545.77, 735.74, 567.01, 381.54, 757.88, 581.51, 424.9, 782.14, 596.31, 446.74, 808.15, 611.57, 464.4, 836.68, 627.34, 480.43, 869.21, 643.61, 495.43, 907.67, 660.35, 509.92, 955.76, 677.59, 524.18, 1021.11, 695.62, 538.53, 1154.84, 715.01, 552.79],
            "End Mass [m/z]":[736.24, 567.5, 382.04, 758.38, 582.01, 425.4, 782.64, 596.81, 447.23, 808.65, 612.07, 464.9, 837.18, 627.84, 480.93, 869.71, 644.1, 495.93, 908.17, 660.85, 510.43, 956.26, 678.09, 524.68, 1021.61, 696.12, 539.03, 1155.34, 715.51, 553.28, 746.84, 574.71, 412.89, 769.91, 589.31, 437.92, 795.37, 604.3, 456.55, 821.93, 619.83, 473.26, 852.43, 635.85, 488.6, 886.99, 652.36, 503.27, 929.36, 669.33, 517.58, 983.17, 686.85, 531.79, 1060.04, 705.39, 546.27, 1250.64, 725.63, 560.3],
            "CE [eV]":['-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
            "W":[11.110000000000014, 7.7000000000000455, 31.360000000000014, 12.039999999999964, 7.7999999999999545, 13.009999999999991, 13.230000000000018, 8.0, 9.810000000000002, 13.779999999999973, 8.270000000000095, 8.849999999999966, 15.75, 8.509999999999991, 8.170000000000016, 17.780000000000086, 8.75, 7.829999999999984, 21.67999999999995, 8.990000000000009, 7.660000000000025, 27.399999999999977, 9.259999999999991, 7.599999999999909, 38.940000000000055, 9.769999999999982, 7.740000000000009, 95.79999999999995, 10.620000000000005, 7.509999999999991, 11.100000000000023, 7.7000000000000455, 31.349999999999966, 12.029999999999973, 7.7999999999999545, 13.020000000000039, 13.230000000000018, 7.990000000000009, 9.810000000000002, 13.779999999999973, 8.259999999999991, 8.860000000000014, 15.75, 8.509999999999991, 8.170000000000016, 17.779999999999973, 8.75, 7.839999999999975, 21.690000000000055, 8.980000000000018, 7.660000000000025, 27.409999999999968, 9.259999999999991, 7.610000000000014, 38.92999999999995, 9.769999999999982, 7.740000000000009, 95.80000000000018, 10.620000000000005, 7.509999999999991],
            "H":[0.15500000000000014, 0.15999999999999992, 0.20500000000000007, 0.17299999999999993, 0.10699999999999998, 0.27, 0.20399999999999996, 0.09599999999999997, 0.29000000000000004, 0.235, 0.09499999999999997, 0.30000000000000004, 0.264, 0.09999999999999998, 0.30600000000000005, 0.28500000000000014, 0.11499999999999988, 0.31000000000000005, 0.30500000000000016, 0.1279999999999999, 0.31700000000000006, 0.32599999999999985, 0.137, 0.32700000000000007, 0.345, 0.14500000000000002, 0.33999999999999997, 0.345, 0.15000000000000002, 0.355, 0.15999999999999992, 0.12, 0.25, 0.18799999999999994, 0.09799999999999998, 0.28400000000000003, 0.21999999999999997, 0.09499999999999997, 0.29500000000000004, 0.25, 0.09699999999999998, 0.30300000000000005, 0.27500000000000013, 0.10699999999999987, 0.30800000000000005, 0.29600000000000004, 0.12, 0.31400000000000006, 0.31600000000000006, 0.134, 0.32000000000000006, 0.33499999999999996, 0.1409999999999999, 0.3340000000000001, 0.345, 0.14800000000000002, 0.347, 0.33999999999999986, 0.15000000000000013, 0.36],
            "xy":[(725.13, 0.965), (559.8, 0.805), (350.68, 0.6), (746.34, 0.977), (574.21, 0.87), (412.39, 0.6), (769.41, 0.986), (588.81, 0.89), (437.42, 0.6), (794.87, 0.995), (603.8, 0.9), (456.05, 0.6), (821.43, 1.006), (619.33, 0.906), (472.76, 0.6), (851.93, 1.025), (635.35, 0.91), (488.1, 0.6), (886.49, 1.045), (651.86, 0.917), (502.77, 0.6), (928.86, 1.064), (668.83, 0.927), (517.08, 0.6), (982.67, 1.085), (686.35, 0.94), (531.29, 0.6), (1059.54, 1.105), (704.89, 0.955), (545.77, 0.6), (735.74, 0.97), (567.01, 0.85), (381.54, 0.6), (757.88, 0.982), (581.51, 0.884), (424.9, 0.6), (782.14, 0.99), (596.31, 0.895), (446.74, 0.6), (808.15, 1.0), (611.57, 0.903), (464.4, 0.6), (836.68, 1.015), (627.34, 0.908), (480.43, 0.6), (869.21, 1.034), (643.61, 0.914), (495.43, 0.6), (907.67, 1.054), (660.35, 0.92), (509.92, 0.6), (955.76, 1.075), (677.59, 0.934), (524.18, 0.6), (1021.11, 1.095), (695.62, 0.947), (538.53, 0.6), (1154.84, 1.11), (715.01, 0.96), (552.79, 0.6)]
        })
        return lubeckdia
    #phospho DIA windows
    def phosphodiawindow():
        phosphodia=pd.DataFrame({
            "#MS Type":['PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF', 'PASEF'],
            "Cycle Id":[1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19],
            "Start IM [1/K0]":[0.8691, 0.6811, 0.8834, 0.691, 0.912, 0.701, 0.9264, 0.7109, 0.9407, 0.7208, 0.9694, 0.7308, 0.9837, 0.7407, 1.0123, 0.7544, 1.0267, 0.7688, 0.7831, 0.7974, 0.8117, 0.8261, 0.8404, 0.8547, 0.8977, 0.955, 0.998, 1.041],
            "End IM [1/K0]":[1.1616, 0.8579, 1.1791, 0.8786, 1.2142, 0.8993, 1.2317, 0.92, 1.2492, 0.9407, 1.2842, 0.9614, 1.3017, 0.9821, 1.3368, 1.0028, 1.3543, 1.0235, 1.0442, 1.0649, 1.0856, 1.1063, 1.1266, 1.1441, 1.1966, 1.2667, 1.3192, 1.3718],
            "Start Mass [m/z]":[839.43, 419.43, 867.43, 447.43, 923.43, 475.43, 951.43, 503.43, 979.43, 531.43, 1035.43, 559.43, 1063.43, 587.43, 1119.43, 615.43, 1147.43, 643.43, 671.43, 699.43, 727.43, 755.43, 783.43, 811.43, 895.43, 1007.43, 1091.43, 1175.43],
            "End Mass [m/z]":[867.43, 447.43, 895.43, 475.43, 951.43, 503.43, 979.43, 531.43, 1007.43, 559.43, 1063.43, 587.43, 1091.43, 615.43, 1147.43, 643.43, 1175.43, 671.43, 699.43, 727.43, 755.43, 783.43, 811.43, 839.43, 923.43, 1035.43, 1119.43, 1203.43],
            "CE [eV]":['-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
            "W":[28.0, 28.0, 28.0, 28.0, 28.0, 28.0, 28.0, 27.999999999999943, 28.0, 28.0, 28.0, 28.0, 28.0, 28.0, 28.0, 28.0, 28.0, 28.0, 28.0, 28.0, 28.0, 28.0, 28.0, 28.0, 28.0, 28.000000000000114, 28.0, 28.0],
            "H":[0.2925, 0.17679999999999996, 0.2957000000000001, 0.1876000000000001, 0.3021999999999999, 0.19830000000000003, 0.3053, 0.20910000000000006, 0.3085000000000001, 0.21989999999999998, 0.31479999999999997, 0.23060000000000003, 0.31800000000000006, 0.24139999999999995, 0.3245, 0.24839999999999995, 0.3276000000000001, 0.25470000000000004, 0.2611, 0.26749999999999996, 0.2738999999999999, 0.2802000000000001, 0.2862, 0.2893999999999999, 0.29890000000000005, 0.3117, 0.32119999999999993, 0.3308],
            "xy":[(839.43, 0.8691), (419.43, 0.6811), (867.43, 0.8834), (447.43, 0.691), (923.43, 0.912), (475.43, 0.701), (951.43, 0.9264), (503.43, 0.7109), (979.43, 0.9407), (531.43, 0.7208), (1035.43, 0.9694), (559.43, 0.7308), (1063.43, 0.9837), (587.43, 0.7407), (1119.43, 1.0123), (615.43, 0.7544), (1147.43, 1.0267), (643.43, 0.7688), (671.43, 0.7831), (699.43, 0.7974), (727.43, 0.8117), (755.43, 0.8261), (783.43, 0.8404), (811.43, 0.8547), (895.43, 0.8977), (1007.43, 0.955), (1091.43, 0.998), (1175.43, 1.041)],
        })
        return phosphodia

    #render ui call for dropdown calling charge states that were detected
    @render.ui
    def chargestates_chargeptmheatmap_ui():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
        mincharge=min(searchoutput["FG.Charge"])
        maxcharge=max(searchoutput["FG.Charge"])
        opts=[item for item in range(mincharge,maxcharge+1)]
        opts.insert(0,0)
        return ui.input_selectize("chargestates_chargeptmheatmap_list","Pick charge to plot data for (use 0 for all):",choices=opts)
    #render ui call for dropdown calling PTMs that were detected
    @render.ui
    def ptm_chargeptmheatmap_ui():
        listofptms=find_ptms()
        ptmshortened=[]
        for i in range(len(listofptms)):
            ptmshortened.append(re.sub(r'\(.*?\)',"",listofptms[i]))
        ptmdict={ptmshortened[i]: listofptms[i] for i in range(len(listofptms))}
        nonedict={"None":"None"}
        ptmdict=(nonedict | ptmdict)
        return ui.input_selectize("ptm_chargeptmheatmap_list","Pick PTM to plot data for (use None for all precursors):",choices=ptmdict,selected="None")

    #Charge/PTM precursor heatmap
    @render.plot(width=1000,height=500)
    def chargeptmheatmap():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()

        charge=input.chargestates_chargeptmheatmap_list()
        ptm=input.ptm_chargeptmheatmap_list()
        numbins_x=input.chargeptm_numbins_x()
        numbins_y=input.chargeptm_numbins_y()
        numbins=[numbins_x,numbins_y]
        cmap=matplotlib.colors.LinearSegmentedColormap.from_list("",["white","blue","red"])
        figsize=(8,6)
        titlefont=input.titlefont()
        axisfont=input.axisfont()

        fig,ax=plt.subplots(figsize=figsize)

        if ptm=="None":
            if charge=="0":
                #all precursors
                his2dsample=searchoutput[["R.Condition","R.Replicate","EG.IonMobility","FG.PrecMz"]]
                title="m/z vs Mobility, Precursor IDs"
                savetitle="All Precursor IDs Heatmap_"
            elif charge!="0":
                #all precursors of specific charge
                his2dsample=searchoutput[searchoutput["FG.Charge"]==int(charge)][["R.Condition","R.Replicate","EG.IonMobility","FG.PrecMz"]]
                title="m/z vs Mobility, "+str(charge)+"+ Precursor IDs"
                savetitle=str(charge)+"+_"+"_Precursor IDs Heatmap_"   
        if ptm!="None":
            if charge=="0":
                #all modified precursors 
                his2dsample=searchoutput[searchoutput["EG.ModifiedPeptide"].str.contains(ptm)][["R.Condition","R.Replicate","EG.IonMobility","FG.PrecMz"]]
                title="m/z vs Mobility, "+ptm+" Precursor IDs"
                savetitle=ptm+"_Precursor IDs Heatmap_"   
            elif charge!="0":
                #modified precursors of specific charge
                his2dsample=searchoutput[(searchoutput["FG.Charge"]==int(charge))&(searchoutput["EG.ModifiedPeptide"].str.contains(ptm))][["R.Condition","R.Replicate","EG.IonMobility","FG.PrecMz"]]
                title="m/z vs Mobility, "+ptm+" "+str(charge)+"+ Precursor IDs"
                savetitle=ptm+"_"+str(charge)+"+_"+"_Precursor IDs Heatmap_"
        j=ax.hist2d(his2dsample["FG.PrecMz"],his2dsample["EG.IonMobility"],bins=numbins,cmap=cmap)
        ax.set_title(title,fontsize=titlefont)
        ax.set_xlabel("m/z",fontsize=axisfont)
        ax.set_ylabel("Ion Mobility ($1/K_{0}$)",fontsize=axisfont)
        ax.tick_params(axis="both",labelsize=axisfont)
        fig.colorbar(j[3],ax=ax)

        #ax.set_ylim(0.6,1.45)
        ax.set_xlim(100,1700)
        
        fig.set_tight_layout(True)
        
        if input.windows_choice()!="None":
            if input.windows_choice()=="lubeck":
                diawindows=lubeckdiawindow()
            elif input.windows_choice()=="phospho":
                diawindows=phosphodiawindow()
            elif input.windows_choice()=="imported":
                diawindows=diawindows_import()

            for i in range(len(diawindows)):
                rect=matplotlib.patches.Rectangle(xy=diawindows["xy"][i],width=diawindows["W"][i],height=diawindows["H"][i],facecolor="red",alpha=0.1,edgecolor="grey")
                ax.add_patch(rect) 
        
        return fig

    #render ui call for dropdown options
    @render.ui
    def charge_ptm_dropdown():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()

        if input.charge_or_ptm()=="charge":
            mincharge=min(searchoutput["FG.Charge"])
            maxcharge=max(searchoutput["FG.Charge"])
            opts=[item for item in range(mincharge,maxcharge+1)]
            return ui.input_selectize("charge_ptm_list","Pick charge to plot data for:",choices=opts)
        if input.charge_or_ptm()=="ptm":
            listofptms=find_ptms()
            ptmshortened=[]
            for i in range(len(listofptms)):
                ptmshortened.append(re.sub(r'\(.*?\)',"",listofptms[i]))
            ptmdict={ptmshortened[i]: listofptms[i] for i in range(len(listofptms))}
            return ui.input_selectize("charge_ptm_list","Pick PTM to plot data for:",choices=ptmdict)

    #scatterplot of picked PTM or charge against the rest of the detected precursors (better for DDA to show charge groups in the heatmap)
    @reactive.effect
    def _():
        @render.plot(width=input.chargeptmscatter_width(),height=input.chargeptmscatter_height())
        def chargeptmscatter():
            searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
            
            titlefont=input.titlefont()
            axisfont=input.axisfont()
            legendfont=input.legendfont()

            if input.charge_or_ptm()=="charge":
                charge=int(input.charge_ptm_list())
                precursor_pick=searchoutput[(searchoutput["FG.Charge"]==charge)==True]
                precursor_other=searchoutput[(searchoutput["FG.Charge"]==charge)==False]
                titlemod=str(charge)+"+ Precursors"
            if input.charge_or_ptm()=="ptm":
                ptm=input.charge_ptm_list()
                precursor_pick=searchoutput[searchoutput["EG.ModifiedPeptide"].str.contains(ptm)==True]
                precursor_other=searchoutput[searchoutput["EG.ModifiedPeptide"].str.contains(ptm)==False]
                titlemod=ptm.split("(")[0]+"Precursors"

            fig,ax=plt.subplots()
            ax.scatter(x=precursor_other["FG.PrecMz"],y=precursor_other["EG.IonMobility"],s=2,label="All Other Precursors")
            ax.scatter(x=precursor_pick["FG.PrecMz"],y=precursor_pick["EG.IonMobility"],s=2,label=titlemod)
            ax.set_xlabel("m/z",fontsize=axisfont)
            ax.set_ylabel("Ion Mobility ($1/K_{0}$)",fontsize=axisfont)
            #ax.set_title(titlemod,fontsize=titlefont)
            ax.legend(loc="upper left",fontsize=legendfont,markerscale=5)
            ax.set_axisbelow(True)
            ax.grid(linestyle="--")

    @render.ui
    def binslider_ui():
        return ui.input_slider("binslider","Number of RT bins:",min=100,max=1000,step=50,value=500,ticks=True)

    #plot # of IDs vs RT for each run
    @reactive.effect
    def _():
        @render.plot(width=input.idsvsrt_width(),height=input.idsvsrt_height())
        def ids_vs_rt():
            searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
            
            rtmax=float(math.ceil(max(searchoutput["EG.ApexRT"]))) #needs to be a float
            numbins=input.binslider()

            bintime=rtmax/numbins*60

            titlefont=input.titlefont()
            axisfont=input.axisfont()
            legendfont=input.legendfont()

            fig,ax=plt.subplots()

            for i in sampleconditions:
                for k in range(max(maxreplicatelist)+1):
                    run=searchoutput[(searchoutput["R.Condition"]==i)&(searchoutput["R.Replicate"]==k)]["EG.ApexRT"]
                    if run.empty:
                        continue
                    hist=np.histogram(run,bins=numbins,range=(0.0,rtmax))
                    ax.plot(np.delete(hist[1],0),hist[0],linewidth=0.5,label=i+"_"+str(k))

            ax.set_ylabel("# of IDs",fontsize=axisfont)
            ax.set_xlabel("RT (min)",fontsize=axisfont)
            ax.tick_params(axis="both",labelsize=axisfont)
            ax.text(0,(ax.get_ylim()[1]-(0.1*ax.get_ylim()[1])),"~"+str(round(bintime,2))+" s per bin",fontsize=axisfont)
            legend=ax.legend(loc='center left', bbox_to_anchor=(1, 0.5),prop={'size':legendfont})
            for i in legend.legend_handles:
                i.set_linewidth(5)
            ax.set_axisbelow(True)
            ax.grid(linestyle="--")
            ax.set_title("# of IDs vs RT",fontsize=titlefont)
            return fig

    @render.ui
    def cond_rep_list_venn1():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
        opts=resultdf["Cond_Rep"].tolist()
        return ui.input_selectize("cond_rep1","Pick first run to compare:",choices=opts)
    @render.ui
    def cond_rep_list_venn2():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
        opts=resultdf["Cond_Rep"].tolist()
        return ui.input_selectize("cond_rep2","Pick second run to compare:",choices=opts)

    #plot venn diagram comparing IDs between runs
    @render.plot
    def venndiagram():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()

        pickA=input.cond_rep1()
        pickB=input.cond_rep2()
        vennpick=input.vennpick()

        conditionA=searchoutput[searchoutput["Cond_Rep"]==(pickA)][["PG.ProteinNames","FG.Charge","PEP.StrippedSequence","EG.ModifiedPeptide"]]
        conditionB=searchoutput[searchoutput["Cond_Rep"]==(pickB)][["PG.ProteinNames","FG.Charge","PEP.StrippedSequence","EG.ModifiedPeptide"]]

        if vennpick=="proteins":
            AvsB=conditionA["PG.ProteinNames"].drop_duplicates().reset_index(drop=True).isin(conditionB["PG.ProteinNames"].drop_duplicates().reset_index(drop=True)).tolist()
            BvsA=conditionB["PG.ProteinNames"].drop_duplicates().reset_index(drop=True).isin(conditionA["PG.ProteinNames"].drop_duplicates().reset_index(drop=True)).tolist()
        elif vennpick=="peptides":
            AvsB=conditionA["EG.ModifiedPeptide"].drop_duplicates().reset_index(drop=True).isin(conditionB["EG.ModifiedPeptide"].drop_duplicates().reset_index(drop=True)).tolist()
            BvsA=conditionB["EG.ModifiedPeptide"].drop_duplicates().reset_index(drop=True).isin(conditionA["EG.ModifiedPeptide"].drop_duplicates().reset_index(drop=True)).tolist()
        elif vennpick=="precursors":
            AvsB=conditionA["EG.ModifiedPeptide"].isin(conditionB["EG.ModifiedPeptide"].drop_duplicates()).tolist()
            BvsA=conditionB["EG.ModifiedPeptide"].isin(conditionA["EG.ModifiedPeptide"].drop_duplicates()).tolist()

        AnotB=sum(1 for i in AvsB if i==False)
        BnotA=sum(1 for i in BvsA if i==False)
        bothAB=sum(1 for i in AvsB if i==True)
        vennlist=[AnotB,BnotA,bothAB]

        fig,ax=plt.subplots()
        venn2(subsets=vennlist,set_labels=(pickA,pickB),set_colors=("tab:blue","tab:orange"),ax=ax)
        venn2_circles(subsets=vennlist,linestyle="dashed",linewidth=0.5)
        plt.title("Venn Diagram for "+vennpick)
        return fig

#endregion

# ============================================================================= PCA
#region

    #compute PCA and plot principal components
    @reactive.effect
    def _():
        @render.plot(width=input.pca_width(),height=input.pca_height())
        def pca_plot():
            #https://www.youtube.com/watch?v=WPRysPAhG5Q&ab_channel=CompuFlair
            searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
            titlefont=input.titlefont()
            axisfont=input.axisfont()
            legendfont=input.legendfont()

            samplelist=searchoutput["Cond_Rep"].drop_duplicates().reset_index(drop=True).tolist()
            intensitydict=dict()
            for run in samplelist:
                intensitydict[run]=searchoutput[searchoutput["Cond_Rep"]==run][["PG.ProteinNames","PG.MS2Quantity"]].drop_duplicates().reset_index(drop=True).rename(columns={"PG.MS2Quantity":run}).set_index(keys="PG.ProteinNames")
            df_intensity=[]
            for run in intensitydict.keys():
                temp_df=intensitydict[run]
                df_intensity.append(temp_df)
            concatenated_proteins=pd.concat(df_intensity,axis=1).dropna()

            X=np.array(concatenated_proteins).T
            pip=Pipeline([("scaler",StandardScaler()),("pca",PCA())]).fit(X)
            X_trans=pip.transform(X)
            #each row is a principal component, each element of each row is a sample

            figsize=(10,5)
            colors=colorpicker()

            fig,ax=plt.subplots(ncols=2,figsize=figsize,gridspec_kw={"width_ratios":[10,5]})
            
            ax1=ax[0]
            ax2=ax[1]

            firstindex=0
            secondindex=0
            for i in range(numconditions):
                if i==0:
                    firstindex=0
                else:
                    firstindex+=repspercondition[i-1]
                secondindex=firstindex+repspercondition[i]
                ax1.scatter(X_trans[firstindex:secondindex,0],X_trans[firstindex:secondindex,1],label=sampleconditions[i],color=colors[i])

            ax1.legend(loc="upper left",bbox_to_anchor=[1,1],fontsize=legendfont)

            ax1.spines['bottom'].set_position('zero')
            ax1.spines['top'].set_color('none')
            ax1.spines['right'].set_color('none')
            ax1.spines['left'].set_position('zero')
            ax1.set_axisbelow(True)
            ax1.grid(linestyle="--")

            ax1.set_xlabel("PC1"+" ("+str(round(pip.named_steps.pca.explained_variance_ratio_[0]*100,1))+"%)",fontsize=axisfont)
            ax1.xaxis.set_label_coords(x=0.5,y=-0.02)
            ax1.set_ylabel("PC2"+" ("+str(round(pip.named_steps.pca.explained_variance_ratio_[1]*100,1))+"%)",fontsize=axisfont)
            ax1.yaxis.set_label_coords(x=-0.02,y=0.45)
            ax1.tick_params(axis="both",labelsize=axisfont)

            ax2.bar(np.arange(1,len(pip.named_steps.pca.explained_variance_ratio_)+1),pip.named_steps.pca.explained_variance_ratio_*100,edgecolor="k")
            ax2.set_xlabel("Principal Component",fontsize=axisfont)
            ax2.set_ylabel("Total % Variance Explained",fontsize=axisfont)
            ax2.set_xticks(np.arange(1,len(pip.named_steps.pca.explained_variance_ratio_)+1))
            ax2.set_axisbelow(True)
            ax2.grid(linestyle="--")
            ax2.tick_params(axis="both",labelsize=axisfont)

            fig.set_tight_layout(True)        

#endregion

# ============================================================================= Mixed Proteome
#region

    @render.text
    def organisminput_readout():
        return input.organisminput()

    @render.text
    def referenceratio_readout():
        return input.referenceratio()
    
    @render.text
    def testratio_readout():
        return input.testratio()

    #plot summed intensities for each organism
    @reactive.effect
    def _():
        @render.plot(width=input.summedintensities_width(),height=input.summedintensities_height())
        def summedintensities():
            searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
            organismlist=list(input.organisminput().split(" "))

            for i in organismlist:
                exec(f'dict_{i}=dict()')
                for j in sampleconditions:
                    for k in range(max(maxreplicatelist)+1):
                        replicatedata=searchoutput[(searchoutput["R.Condition"]==j)&(searchoutput["R.Replicate"]==k)]
                        if replicatedata.empty:
                            continue
                        exec(f'dict_{i}["{j}_{k}"]=replicatedata[["PG.ProteinNames","PG.MS2Quantity"]].drop_duplicates().reset_index(drop=True)')
                        exec(f'dict_{i}["{j}_{k}"]=dict_{i}["{j}_{k}"][dict_{i}["{j}_{k}"]["PG.ProteinNames"].str.contains(i)&(dict_{i}["{j}_{k}"]["PG.MS2Quantity"]>0)].reset_index(drop=True)')

            samplekeys=resultdf["Cond_Rep"].tolist()
            intensitysumdf=pd.DataFrame(index=samplekeys)
            for i in organismlist:
                exec(f'organismdict=dict_{i}')
                exec(f'intensitylist_{i}=[]')
                for condition in samplekeys:
                    exec(f'intensitylist_{i}.append(dict_{i}[condition]["PG.MS2Quantity"].sum())')
                exec(f'intensitysumdf[i]=intensitylist_{i}')
            
            figsize=(5,5)
            titlefont=input.titlefont()
            axisfont=input.axisfont()
            labelfont=input.labelfont()

            matplottabcolors=list(mcolors.TABLEAU_COLORS)
            bluegray_colors=["#054169","#0071BC","#737373"]

            if input.coloroptions_sumint()=="matplot":
                colors=matplottabcolors
            elif input.coloroptions_sumint()=="bluegray":
                colors=bluegray_colors

            x=np.arange(len(intensitysumdf.index))
            fig,ax=plt.subplots(figsize=figsize)
            ax.bar(x,intensitysumdf[organismlist[0]],label=organismlist[0],color=colors[0])
            ax.bar(x,intensitysumdf[organismlist[1]],bottom=intensitysumdf[organismlist[0]],label=organismlist[1],color=colors[1])
            ax.bar(x,intensitysumdf[organismlist[2]],bottom=intensitysumdf[organismlist[0]]+intensitysumdf[organismlist[1]],label=organismlist[2],color=colors[2])

            ax.set_xticks(x,labels=intensitysumdf.index,rotation=90,fontsize=axisfont)
            ax.tick_params(axis="y",labelsize=axisfont)
            ax.set_ylabel("Total Intensity",fontsize=axisfont)
            ax.legend(loc="center left",bbox_to_anchor=(1, 0.5),fontsize=axisfont)
            ax.set_axisbelow(True)
            ax.grid(linestyle="--")
            ax.set_title("Total Intensity per Organism per Run",fontsize=titlefont)
            return fig

    #plot protein counts per organism
    @reactive.effect
    def _():
        @render.plot(width=input.countsperorganism_width(),height=input.countsperorganism_height())
        def countsperorganism():
            searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
            organismlist=list(input.organisminput().split(" "))
            samplekeys=resultdf["Cond_Rep"].tolist()

            if input.countsplotinput()=="proteins":
                for i in organismlist:
                    exec(f'dict_{i}=dict()')
                    for j in sampleconditions:
                        for k in range(max(maxreplicatelist)+1):
                            replicatedata=searchoutput[(searchoutput["R.Condition"]==j)&(searchoutput["R.Replicate"]==k)]
                            if replicatedata.empty:
                                continue
                            exec(f'dict_{i}["{j}_{k}"]=replicatedata[["PG.ProteinNames","PG.MS2Quantity"]].drop_duplicates().reset_index(drop=True)')
                            exec(f'dict_{i}["{j}_{k}"]=dict_{i}["{j}_{k}"][dict_{i}["{j}_{k}"]["PG.ProteinNames"].str.contains(i)&(dict_{i}["{j}_{k}"]["PG.MS2Quantity"]>0)].reset_index(drop=True)')
                y_padding=0.25
                titleprop="Protein"
            if input.countsplotinput()=="peptides":
                for i in organismlist:
                    exec(f'dict_{i}=dict()')
                    for j in sampleconditions:
                        for k in range(max(maxreplicatelist)+1):
                            replicatedata=searchoutput[(searchoutput["R.Condition"]==j)&(searchoutput["R.Replicate"]==k)]
                            if replicatedata.empty:
                                continue
                            exec(f'dict_{i}["{j}_{k}"]=replicatedata[["PG.ProteinNames","PEP.StrippedSequence"]].drop_duplicates().reset_index(drop=True)')
                            exec(f'dict_{i}["{j}_{k}"]=dict_{i}["{j}_{k}"][dict_{i}["{j}_{k}"]["PG.ProteinNames"].str.contains(i)].reset_index(drop=True)')
                y_padding=0.45
                titleprop="Peptide"
            if input.countsplotinput()=="precursors":
                for i in organismlist:
                    exec(f'dict_{i}=dict()')
                    for j in sampleconditions:
                        for k in range(max(maxreplicatelist)+1):
                            replicatedata=searchoutput[(searchoutput["R.Condition"]==j)&(searchoutput["R.Replicate"]==k)]
                            if replicatedata.empty:
                                continue
                            exec(f'dict_{i}["{j}_{k}"]=replicatedata[["PG.ProteinNames","EG.ModifiedPeptide","FG.MS2Quantity"]].drop_duplicates().reset_index(drop=True)')
                            exec(f'dict_{i}["{j}_{k}"]=dict_{i}["{j}_{k}"][dict_{i}["{j}_{k}"]["PG.ProteinNames"].str.contains(i)&(dict_{i}["{j}_{k}"]["FG.MS2Quantity"]>0)].reset_index(drop=True)')
                y_padding=0.45
                titleprop="Precursor"
           
            countdf=pd.DataFrame(index=samplekeys)
            for i in organismlist:
                exec(f'organismdict=dict_{i}')
                exec(f'list_{i}=[]')
                for condition in samplekeys:
                    exec(f'list_{i}.append(len(organismdict[condition]))')
                exec(f'countdf[i]=list_{i}')

            figsize=(10,5)
            titlefont=input.titlefont()
            axisfont=input.axisfont()
            labelfont=input.labelfont()
            legendfont=input.legendfont()

            matplottabcolors=list(mcolors.TABLEAU_COLORS)
            bluegray_colors=["#054169","#0071BC","#737373"]

            if input.coloroptions_sumint()=="matplot":
                colors=matplottabcolors
            elif input.coloroptions_sumint()=="bluegray":
                colors=bluegray_colors

            n=len(samplekeys)
            x=np.arange(n)
            width=0.25

            fig,ax=plt.subplots(figsize=figsize)
            for i in range(len(organismlist)):
                ax.bar(x+(i*width),countdf[organismlist[i]],width=width,label=organismlist[i],color=colors[i])
                ax.bar_label(ax.containers[i],label_type="edge",rotation=90,padding=5,fontsize=labelfont)

            ax.set_xticks(x+width,samplekeys,rotation=90)
            ax.tick_params(axis='both',labelsize=axisfont)
            ax.set_ylim(top=max(countdf[organismlist[0]])+(y_padding)*max(countdf[organismlist[0]]))
            ax.set_axisbelow(True)
            ax.grid(linestyle="--")
            ax.legend(loc='center left', bbox_to_anchor=(1, 0.5),prop={'size':legendfont})
            ax.set_ylabel("Counts",fontsize=axisfont)
            ax.set_title(titleprop+" Counts per Organism",fontsize=titlefont)              
            return fig

    #render ui call for dropdown calling sample condition names
    @render.ui
    def referencecondition():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
        opts=sampleconditions
        return ui.input_selectize("referencecondition_list","Pick reference condition:",choices=opts,selected=opts[0])
    #render ui call for dropdown calling sample condition names
    @render.ui
    def testcondition():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
        opts=sampleconditions
        return ui.input_selectize("testcondition_list","Pick test condition:",choices=opts,selected=opts[1])
    @render.text
    def organismreminder():
        return "Organisms in order: "+input.organisminput()

    @render.text
    def expectedratios_note():
        return "Note: average ratios will be shown as a dashed line and expected ratios input in the text boxes below will be shown as a solid line"
    #plot quant ratios for each organism
    @render.plot(width=1200,height=600)
    def quantratios():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()

        organismlist=list(input.organisminput().split(" "))

        control=input.referencecondition_list()
        test=input.testcondition_list()
        
        referenceratios=[int(x) for x in input.referenceratio().split()]
        testratios=[int(x) for x in input.testratio().split()]
        expectedratios=[]
        for i in range(len(referenceratios)):
            expectedratios.append(np.log2(testratios[i]/referenceratios[i]))

        figsize=(10,5)
        titlefont=input.titlefont()
        axisfont=input.axisfont()
        labelfont=input.labelfont()
        legendfont=input.legendfont()
        y_padding=0.2

        matplottabcolors=list(mcolors.TABLEAU_COLORS)
        bluegray_colors=["#054169","#0071BC","#737373"]

        if input.coloroptions_sumint()=="matplot":
            colors=matplottabcolors
        elif input.coloroptions_sumint()=="bluegray":
            colors=bluegray_colors

        cvcutoff=input.cvcutofflevel()

        for i in organismlist:
            exec(f'dict_{i}=dict()')
            for j in sampleconditions:
                for k in range(max(maxreplicatelist)+1):
                    replicatedata=searchoutput[(searchoutput["R.Condition"]==j)&(searchoutput["R.Replicate"]==k)]
                    if replicatedata.empty:
                        continue
                    exec(f'dict_{i}["{j}_{k}"]=replicatedata[["PG.ProteinNames","PG.MS2Quantity"]].drop_duplicates().reset_index(drop=True)')
                    exec(f'dict_{i}["{j}_{k}"]=dict_{i}["{j}_{k}"][dict_{i}["{j}_{k}"]["PG.ProteinNames"].str.contains(i)&(dict_{i}["{j}_{k}"]["PG.MS2Quantity"]>0)].reset_index(drop=True)')

        for organism in organismlist:
            listofdfs=[]
            for condition in sampleconditions:
                tempdfs=[]
                for replicate in range(max(maxreplicatelist)+1):
                    if replicate==0:
                        continue
                    exec(f'tempdf_{replicate}=dict_{organism}["{condition}_{replicate}"].set_index("PG.ProteinNames")')
                    exec(f'tempdfs.append(tempdf_{replicate})')
                exec(f'listofdfs.append(pd.concat(tempdfs,axis=1,join="outer").loc[:,["PG.MS2Quantity"]].mean(axis=1))')
            exec(f'df_{organism}=pd.concat(listofdfs,axis=1)')
            exec(f'df_{organism}.columns=sampleconditions')

        for organism in organismlist:
            listofdfs=[]
            for condition in sampleconditions:
                tempdfs=[]
                for replicate in range(max(maxreplicatelist)+1):
                    if replicate==0:
                        continue
                    exec(f'tempdf_{replicate}=dict_{organism}["{condition}_{replicate}"].set_index("PG.ProteinNames")')
                    exec(f'tempdfs.append(tempdf_{replicate})')
                exec(f'listofdfs.append(pd.concat(tempdfs,axis=1,join="outer").loc[:,["PG.MS2Quantity"]].std(axis=1))')
            exec(f'df_{organism}_stdev=pd.concat(listofdfs,axis=1)')
            exec(f'df_{organism}_stdev.columns=sampleconditions')
            
        for organism in organismlist:
            for condition in sampleconditions:
                exec(f'df_{organism}["{condition}_CV"]=df_{organism}_stdev["{condition}"]/df_{organism}["{condition}"]*100')

        if input.cvcutoff_switch()==True:
            for organism in organismlist:
                exec(f'df_{organism}.drop(df_{organism}[(df_{organism}[test+"_CV"]>cvcutoff) | (df_{organism}[test+"_CV"]>cvcutoff)].index,inplace=True)')

        organismratioaverage=[]
        organismratiostdev=[]
        for organism in organismlist:
            exec(f'merged_{organism}=df_{organism}[test].reset_index().dropna().merge(df_{organism}[control].reset_index().dropna(),how="inner")')
            exec(f'log2ratio_{organism}=np.log2(merged_{organism}[test]/merged_{organism}[control])')
            exec(f'merged_log10_{organism}=np.log10(merged_{organism}[[test,control]])')
            exec(f'experimentalratio_{organism}=np.average(log2ratio_{organism})')
            
            exec(f'organismratioaverage.append(np.mean(log2ratio_{organism}))')
            exec(f'organismratiostdev.append(np.std(log2ratio_{organism}))')

        fig,ax=plt.subplots(nrows=1,ncols=3,figsize=figsize,gridspec_kw={"width_ratios":[2,5,2]})

        x=0
        for organism in organismlist:
            exec(f'ax[0].bar(x,len(merged_{organism}),color=colors[x])')
            ax[0].bar_label(ax[0].containers[x],label_type="edge",rotation=90,padding=5,fontsize=labelfont)
            exec(f'ax[1].scatter(merged_log10_{organism}[control],log2ratio_{organism},alpha=0.25,color=colors[x])')
            exec(f'ax[2].hist(log2ratio_{organism},bins=100,orientation=u"horizontal",alpha=0.5,density=True,color=colors[x])')
            x=x+1

        ax[0].set_xticks(np.arange(len(organismlist)),organismlist,rotation=90)
        ax[0].set_ylabel("Number of Proteins",fontsize=axisfont)
        bottom,top=ax[0].get_ylim()
        ax[0].set_ylim(top=top+(y_padding*top))
        ax[0].tick_params(axis="both",labelsize=axisfont)

        leg=ax[1].legend(organismlist,loc="upper right",prop={'size':legendfont})
        for tag in leg.legend_handles:
            tag.set_alpha(1)
        ax[1].set_xlabel("log10 Intensity, Reference",fontsize=axisfont)
        ax[1].set_ylabel("log2 Ratio, Test/Reference",fontsize=axisfont)
        ax[1].set_title("Reference: "+control+", Test: "+test,pad=10,fontsize=titlefont)
        ax[1].tick_params(axis="both",labelsize=axisfont)

        ax[2].set_xlabel("Density",fontsize=axisfont)
        ax[2].set_ylabel("log2 Ratio, Test/Reference",fontsize=axisfont)
        ax[2].tick_params(axis="both",labelsize=axisfont)

        if input.plotrange_switch()==True:
            ymin=input.plotrange()[0]
            ymax=input.plotrange()[1]
            ax[1].set_ylim(ymin,ymax)
            ax[2].set_ylim(ymin,ymax)
        
        for i in range(3):  
            ax[i].set_axisbelow(True)
            ax[i].grid(linestyle="--")

        for i in range(len(expectedratios)):
            ax[1].axhline(y=expectedratios[i],color=colors[i])
            ax[2].axhline(y=expectedratios[i],color=colors[i])

        for i in range(len(organismratioaverage)):
            ax[1].axhline(y=organismratioaverage[i],color=colors[i],linestyle="dashed")
            ax[2].axhline(y=organismratioaverage[i],color=colors[i],linestyle="dashed")
            
        fig.set_tight_layout(True)

#endregion

# ============================================================================= PRM
#region

    #import prm list and generate a searchoutput-like table for just the prm peptides
    @reactive.calc
    def prm_import():
        if input.prm_list() is None:
            return pd.DataFrame()
        prm_list=pd.read_csv(input.prm_list()[0]["datapath"])
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
        df_list=[]
        for peptide in prm_list["EG.ModifiedPeptide"]:
            prm_peptide=searchoutput[searchoutput["EG.ModifiedPeptide"]==peptide]
            df_list.append(prm_peptide)
        searchoutput_prmpepts=pd.concat(df_list).reset_index(drop=True)
        if "Concentration" in searchoutput.columns:
            searchoutput_prmpepts.sort_values("Concentration")
        return prm_list,searchoutput_prmpepts

    #prm selectize peptide list
    @render.ui
    def prmpeptracker_pick():
        prm_list,searchoutput_prmpepts=prm_import()
        opts=prm_list["EG.ModifiedPeptide"]
        return ui.input_selectize("prmpeptracker_picklist","Pick PRM peptide to plot data for:",choices=opts,width="600px")

    #plot intensity across runs, number of replicates, and CVs of selected peptide from prm list
    @reactive.effect
    def _():
        @render.plot(width=input.prmpeptracker_width(),height=input.prmpeptracker_height())
        def prmpeptracker_plot():
            searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
            prm_list,searchoutput_prmpepts=prm_import()

            peplist=prm_list["EG.ModifiedPeptide"]
            peptide=peplist[int(input.prmpeptracker_picklist())]

            pepdf=searchoutput_prmpepts[searchoutput_prmpepts["EG.ModifiedPeptide"]==peptide]
            chargelist=pepdf["FG.Charge"].drop_duplicates().tolist()

            titlefont=input.titlefont()

            fig,ax=plt.subplots(ncols=2,nrows=2)
            for i,charge in enumerate(chargelist):
                meandf=pepdf[pepdf["FG.Charge"]==charge][["R.Condition","FG.MS2Quantity"]].groupby("R.Condition").mean()
                stdev=pepdf[pepdf["FG.Charge"]==charge][["R.Condition","FG.MS2Quantity"]].groupby("R.Condition").std()
                cv=stdev/meandf*100
                meandf=meandf.reset_index()
                stdev=stdev.reset_index()
                cv=cv.reset_index()
                x=np.arange(0,len(meandf["R.Condition"]),1)
                y=meandf["FG.MS2Quantity"].tolist()
                fit=np.poly1d(np.polyfit(x,y,1))
                ax[0,0].errorbar(x,y,yerr=stdev["FG.MS2Quantity"],marker="o",linestyle="None")
                ax[0,0].plot(x,fit(x),linestyle="--",color="black")
                ax[0,0].set_ylabel("FG.MS2Quantity")
                
                width=0.25
                detectedinreps=pepdf[pepdf["FG.Charge"]==charge].groupby("R.Condition").size().tolist()
                ax[0,1].bar(x+i*width,detectedinreps,width=width,label=str(charge)+"+")
                ax[0,1].set_xticks(x+((len(meandf["R.Condition"])-1)/2)*width,meandf["R.Condition"])
                ax[0,1].set_ylabel("Number of Replicates")

                ax[1,0].plot(meandf["R.Condition"],cv["FG.MS2Quantity"],marker="o")
                ax[1,0].axhline(y=20,linestyle="--",color="black")
                ax[1,0].set_ylabel("CV (%)")
                
                if "Concentration" in searchoutput.columns:
                    concentrationlist=pepdf[pepdf["FG.Charge"]==charge]["Concentration"].tolist()
                    expectratio=[]
                    for conc in concentrationlist:
                        conc_min=min(concentrationlist)
                        expectratio.append(conc/conc_min)

                    measuredratio=[]
                    signallist=pepdf[pepdf["FG.Charge"]==charge]["FG.MS2Quantity"]
                    for signal in signallist:
                        conc_min=min(signallist)
                        measuredratio.append(signal/conc_min)
                    ax[1,1].scatter(expectratio,measuredratio)
                    ax[1,1].set_xlabel("Expected Ratio")
                    ax[1,1].set_ylabel("Measured Ratio")
                else:
                    ax[1,1].set_visible(False)

            ax[0,0].set_title("Intensity Across Runs")
            ax[0,0].set_axisbelow(True)
            ax[0,0].grid(linestyle="--")

            ax[0,1].set_title("Number of Replicates Observed")
            ax[0,1].set_axisbelow(True)
            ax[0,1].grid(linestyle="--")

            ax[1,0].set_title("CVs")
            ax[1,0].set_axisbelow(True)
            ax[1,0].grid(linestyle="--")

            ax[1,1].set_title("Dilution Curve")
            ax[1,1].set_axisbelow(True)
            ax[1,1].grid(linestyle="--")

            fig.legend(loc="lower right",bbox_to_anchor=(0.99,0.9))
            fig.suptitle(peptide.strip("_"),fontsize=titlefont)
            fig.set_tight_layout(True)

    #plot intensity of all prm peptides across runs
    @reactive.effect
    def _():
        @render.plot(width=input.prmpepintensity_width(),height=input.prmpepintensity_height())
        def prmpepintensity_plot():
            searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
            prm_list,searchoutput_prmpepts=prm_import()

            df_list=[]
            for peptide in prm_list["EG.ModifiedPeptide"]:
                prm_peptide=searchoutput[searchoutput["EG.ModifiedPeptide"]==peptide]
                df_list.append(prm_peptide)
            searchoutput_prmpepts=pd.concat(df_list).reset_index(drop=True)

            axisfont=input.axisfont()
            legendfont=input.legendfont()

            fig,ax=plt.subplots()
            for peptide in prm_list["EG.ModifiedPeptide"]:
                pepdf=searchoutput_prmpepts[searchoutput_prmpepts["EG.ModifiedPeptide"]==peptide]
                chargelist=pepdf["FG.Charge"].drop_duplicates().tolist()
                for charge in chargelist:
                    ax.plot(pepdf[pepdf["FG.Charge"]==charge]["Cond_Rep"],np.log10(pepdf[pepdf["FG.Charge"]==charge]["FG.MS2Quantity"]),marker="o",label=peptide.strip("_")+"_"+str(charge)+"+")
            ax.legend(loc='center left', bbox_to_anchor=(1,0.5),prop={'size':legendfont})
            ax.tick_params(axis="x",rotation=90,labelsize=axisfont)
            ax.tick_params(axis="y",labelsize=axisfont)
            ax.set_xlabel("Condition",fontsize=axisfont)
            ax.set_ylabel("log10(FG.MS2Quantity)",fontsize=axisfont)
            ax.set_axisbelow(True)
            ax.grid(linestyle="--")

    #generate prm table to be exported to timscontrol
    @reactive.calc
    def prm_list_import():
        if input.prm_list() is None:
            return pd.DataFrame()
        prm_list=pd.read_csv(input.prm_list()[0]["datapath"])
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
        try:
            isolationwidth=float(input.isolationwidth_input())
        except:
            isolationwidth=0
        try:
            rtwindow=float(input.rtwindow_input())
        except:
            rtwindow=0
        try:
            imwindow=float(input.imwindow_input())
        except:
            imwindow=0
        df_list=[]
        for peptide in prm_list["EG.ModifiedPeptide"]:
            prm_peptide=searchoutput[searchoutput["EG.ModifiedPeptide"]==peptide][["PG.ProteinNames","EG.ModifiedPeptide","FG.PrecMz","FG.Charge","EG.ApexRT","EG.IonMobility"]].groupby(["PG.ProteinNames","EG.ModifiedPeptide","FG.Charge"]).mean().reset_index()
            df_list.append(prm_peptide)
        searchoutput_prm=pd.concat(df_list).reset_index(drop=True)
        searchoutput_prm["EG.ApexRT"]=searchoutput_prm["EG.ApexRT"]*60

        searchoutput_prm.rename(columns={"FG.PrecMz":"Mass [m/z]","FG.Charge":"Charge","EG.ApexRT":"RT [s]"},inplace=True)

        mzisolationwidth=[]
        RTrange=[]
        startIM=[]
        endIM=[]
        CE=[]
        externalID=[]
        description=[]
        for i in range(len(searchoutput_prm)):
            mzisolationwidth.append(isolationwidth)
            RTrange.append(rtwindow)
            startIM.append(searchoutput_prm["EG.IonMobility"][i]-imwindow)
            endIM.append(searchoutput_prm["EG.IonMobility"][i]+imwindow)
            CE.append("")
            externalID.append(searchoutput_prm["EG.ModifiedPeptide"][i])
            description.append("")

        searchoutput_prm["Isolation Width [m/z]"]=mzisolationwidth
        searchoutput_prm["RT Range [s]"]=RTrange
        searchoutput_prm["Start IM [1/k0]"]=startIM
        searchoutput_prm["End IM [1/k0]"]=endIM
        searchoutput_prm["CE [eV]"]=CE
        searchoutput_prm["External ID"]=externalID
        searchoutput_prm["Description"]=description

        searchoutput_prm=searchoutput_prm[["Mass [m/z]","Charge","Isolation Width [m/z]","RT [s]","RT Range [s]","Start IM [1/k0]","End IM [1/k0]","CE [eV]","External ID","Description","PG.ProteinNames","EG.ModifiedPeptide","EG.IonMobility"]]

        searchoutput_prm.drop(columns=["PG.ProteinNames","EG.ModifiedPeptide","EG.IonMobility"],inplace=True)

        return searchoutput_prm
    
    #show prm list in window
    @render.data_frame
    def prm_table():
        searchoutput_prm=prm_list_import()
        return render.DataGrid(searchoutput_prm,width="100%",editable=True)

    #download prm list that's been edited in the window
    @render.download(filename="prm_peptide_list.csv")
    def prm_table_download():
        prm_table_view=prm_table.data_view()
        
        yield prm_table_view.to_csv(index=False)

#endregion

# ============================================================================= Dilution Series
#region

    @render.ui
    def normalizingcondition():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
        opts=sampleconditions
        return ui.input_selectize("normalizingcondition_pick","Pick normalizing condition",choices=opts)

    @reactive.effect
    def _():
        @render.plot()
        def dilutionseries_plot(width=input.dilutionseries_width(),height=input.dilutionseries_height()):
            searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
            sortedconditions=[]
            concentrations=searchoutput["Concentration"].drop_duplicates().tolist()
            sortedconcentrations=sorted(concentrations)
            for i in sortedconcentrations:
                sortedconditions.append(searchoutput[searchoutput["Concentration"]==i]["R.Condition"].values[0])

            normalizingcondition=input.normalizingcondition_pick()

            dilutionseries=[]
            for condition in sortedconditions:
                norm=searchoutput[searchoutput["R.Condition"]==normalizingcondition][["PG.ProteinNames","PG.MS2Quantity"]].groupby("PG.ProteinNames").mean().reset_index()
                test=searchoutput[searchoutput["R.Condition"]==condition][["PG.ProteinNames","PG.MS2Quantity"]].groupby("PG.ProteinNames").mean().reset_index()

                merge=norm.merge(test,how="left",on="PG.ProteinNames",suffixes=("_norm","_test"))
                merge["Ratio"]=merge["PG.MS2Quantity_test"]/merge["PG.MS2Quantity_norm"]
                merge=merge.dropna()
                dilutionseries.append(merge["Ratio"])

            fig,ax=plt.subplots()

            medianlineprops=dict(linestyle="--",color="black")
            flierprops=dict(markersize=3)

            bplot=ax.boxplot(dilutionseries,medianprops=medianlineprops,flierprops=flierprops)
            plot=ax.violinplot(dilutionseries,showextrema=False)

            ax.set_yscale("log")
            ax.set_xticks(np.arange(1,len(sortedconditions)+1,1),labels=sortedconditions)
            ax.set_xlabel("Condition")
            ax.set_ylabel("Ratio")
            ax.set_axisbelow(True)
            ax.grid(linestyle="--")

            colors=colorpicker()
            for z,color in zip(plot["bodies"],colors):
                z.set_facecolor(color)
                z.set_edgecolor("black")
                z.set_alpha(0.7)   

#endregion

# ============================================================================= Raw Data
#region

    #take text input for data paths and make dictionaries of frame data
    @reactive.calc
    def rawfile_list():
        filelist=list(input.rawfile_input().split("\n"))
        MSframedict=dict()
        precursordict=dict()
        samplenames=[]
        for run in filelist:
            frames=pd.DataFrame(atb.read_bruker_sql(run)[2])
            MSframedict[run]=frames[frames["MsMsType"]==0].reset_index(drop=True)
            precursordict[run]=pd.DataFrame(atb.read_bruker_sql(run)[3])
            samplenames.append(run.split("\\")[-1])
        return MSframedict,precursordict,samplenames        

    #render ui for checkboxes to plot specific runs
    @render.ui
    def rawfile_checkboxes_tic():
        MSframedict,precursordict,samplenames=rawfile_list()
        opts=dict()
        keys=input.rawfile_input().split("\n")
        labels=samplenames
        for x,y in zip(keys,labels):
            opts[x]=y
        return ui.input_checkbox_group("rawfile_pick_tic","Pick files to plot data for:",choices=opts,width="800px")
    #plot TIC from raw data
    @reactive.effect
    def _():
        @render.plot(width=input.tic_width(),height=input.tic_height())
        def TIC_plot():
            MSframedict,precursordict,samplenames=rawfile_list()
            checkgroup=input.rawfile_pick_tic()
            colors=list(mcolors.TABLEAU_COLORS)
            if input.stacked_tic()==True:
                fig,ax=plt.subplots(nrows=len(checkgroup),sharex=True)
                for i,run in enumerate(checkgroup):
                    x=MSframedict[run]["Time"]/60
                    y=MSframedict[run]["SummedIntensities"]
                    ax[i].plot(x,y,label=run.split("\\")[-1],linewidth=1.5,color=colors[i])
                    ax[i].set_ylabel("Intensity")
                    ax[i].set_axisbelow(True)
                    ax[i].grid(linestyle="--")
                    legend=ax[i].legend(loc="upper left")
                    for z in legend.legend_handles:
                        z.set_linewidth(5)
            else:
                fig,ax=plt.subplots()
                for run in checkgroup:
                    x=MSframedict[run]["Time"]/60
                    y=MSframedict[run]["SummedIntensities"]
                    ax.plot(x,y,label=run.split("\\")[-1],linewidth=0.75)
                ax.set_xlabel("Time (min)")
                ax.set_ylabel("Intensity")
                ax.set_axisbelow(True)
                ax.grid(linestyle="--")
                #legend=ax.legend(loc='center left', bbox_to_anchor=(1,0.5),prop={'size':10})
                legend=ax.legend(loc="upper left")
                for z in legend.legend_handles:
                    z.set_linewidth(5)
        
    #render ui for checkboxes to plot specific runs
    @render.ui
    def rawfile_checkboxes_bpc():
        MSframedict,precursordict,samplenames=rawfile_list()
        opts=dict()
        keys=input.rawfile_input().split("\n")
        labels=samplenames
        for x,y in zip(keys,labels):
            opts[x]=y
        return ui.input_checkbox_group("rawfile_pick_bpc","Pick files to plot data for:",choices=opts,width="800px")
    #plot BPC from raw data
    @reactive.effect
    def _():
        @render.plot(width=input.bpc_width(),height=input.bpc_height())
        def BPC_plot():
            MSframedict,precursordict,samplenames=rawfile_list()
            checkgroup=input.rawfile_pick_bpc()
            colors=list(mcolors.TABLEAU_COLORS)
            if input.stacked_bpc()==True:
                fig,ax=plt.subplots(nrows=len(checkgroup),sharex=True)
                for i,run in enumerate(checkgroup):
                    x=MSframedict[run]["Time"]/60
                    y=MSframedict[run]["MaxIntensity"]
                    ax[i].plot(x,y,label=run.split("\\")[-1],linewidth=1.5,color=colors[i])
                    ax[i].set_ylabel("Intensity")
                    ax[i].set_axisbelow(True)
                    ax[i].grid(linestyle="--")
                    legend=ax[i].legend(loc="upper left")
                    for z in legend.legend_handles:
                        z.set_linewidth(5)
            else:
                fig,ax=plt.subplots()
                for run in checkgroup:
                    x=MSframedict[run]["Time"]/60
                    y=MSframedict[run]["MaxIntensity"]
                    ax.plot(x,y,label=run.split("\\")[-1],linewidth=0.75)
                ax.set_xlabel("Time (min)")
                ax.set_ylabel("Intensity")
                ax.set_axisbelow(True)
                ax.grid(linestyle="--")
                #legend=ax.legend(loc='center left', bbox_to_anchor=(1,0.5),prop={'size':10})
                legend=ax.legend(loc='upper left')
                for z in legend.legend_handles:
                    z.set_linewidth(5)      

    #render ui for checkboxes to plot specific runs
    @render.ui
    def rawfile_checkboxes_accutime():
        MSframedict,precursordict,samplenames=rawfile_list()
        opts=dict()
        keys=input.rawfile_input().split("\n")
        labels=samplenames
        for x,y in zip(keys,labels):
            opts[x]=y
        return ui.input_checkbox_group("rawfile_pick_accutime","Pick files to plot data for:",choices=opts,width="800px")
    #plot accumulation time from raw data
    @reactive.effect
    def _():
        @render.plot(width=input.accutime_width(),height=input.accutime_height())
        def accutime_plot():
            MSframedict,precursordict,samplenames=rawfile_list()
            checkgroup=input.rawfile_pick_accutime()
            colors=list(mcolors.TABLEAU_COLORS)
            if input.stacked_accutime()==True:
                fig,ax=plt.subplots(nrows=len(checkgroup),sharex=True)
                for i,run in enumerate(checkgroup):
                    x=MSframedict[run]["Time"]/60
                    y=MSframedict[run]["AccumulationTime"]
                    ax[i].plot(x,y,label=run.split("\\")[-1],linewidth=1.5,color=colors[i])
                    ax[i].set_ylabel("Accumulation Time (ms)")
                    ax[i].set_axisbelow(True)
                    ax[i].grid(linestyle="--")
                    legend=ax[i].legend(loc="upper left")
                    for z in legend.legend_handles:
                        z.set_linewidth(5)
            else:
                fig,ax=plt.subplots()
                for run in checkgroup:
                    x=MSframedict[run]["Time"]/60
                    y=MSframedict[run]["AccumulationTime"]
                    ax.plot(x,y,label=run.split("\\")[-1],linewidth=0.75)
                ax.set_xlabel("Time (min)")
                ax.set_ylabel("Accumulation Time (ms)")
                ax.set_axisbelow(True)
                ax.grid(linestyle="--")
                legend=ax.legend(loc='center left', bbox_to_anchor=(1,0.5),prop={'size':10})
                for z in legend.legend_handles:
                    z.set_linewidth(5)

    @render.ui
    def rawfile_buttons_eic():
        MSframedict,precursordict,samplenames=rawfile_list()
        opts=dict()
        keys=input.rawfile_input().split("\n")
        labels=samplenames
        for x,y in zip(keys,labels):
            opts[x]=y
        return ui.input_radio_buttons("rawfile_pick_eic","Pick file to plot data for:",choices=opts,width="800px")
    
    #input for mobility add-on for EICs
    @render.ui
    def mobility_input():
        if input.include_mobility()==True:
            return ui.input_text("mobility_input_value","Input mobility for EIC:"),ui.input_text("mobility_input_window","Input mobility window (1/k0) for EIC:")
        
    @reactive.calc
    @reactive.event(input.load_eic)
    def eic_setup():
        mz=float(input.eic_mz_input())
        ppm_error=float(input.eic_ppm_input())
        rawfile=atb.TimsTOF(input.rawfile_pick_eic())

        low_mz=mz/(1+ppm_error/10**6)
        high_mz=mz*(1+ppm_error/10**6)

        if input.include_mobility()==True:
            mobility=float(input.mobility_input_value())
            window=float(input.mobility_input_window())
            low_mobility=mobility-window
            high_mobility=mobility+window
            eic_df=rawfile[:,low_mobility: high_mobility,0,low_mz: high_mz]
        else:
            eic_df=rawfile[:,:,0,low_mz: high_mz]

        return eic_df

    #plot EIC for input mass
    @reactive.effect
    def _():
        @render.plot(width=input.eic_width(),height=input.eic_height())
        def eic():
            eic_df=eic_setup()
            fig,ax=plt.subplots(figsize=(10,5))
            ax.plot(eic_df["rt_values_min"],eic_df["intensity_values"],linewidth=0.5)
            ax.set_xlabel("Time (min)")
            ax.set_ylabel("Intensity")
            if input.include_mobility()==True:
                ax.set_title(input.rawfile_pick_eic().split("\\")[-1]+"\n"+"EIC: "+str(input.eic_mz_input())+", Mobility: "+str(input.mobility_input_value()))
            else:
                ax.set_title(input.rawfile_pick_eic().split("\\")[-1]+"\n"+"EIC: "+str(input.eic_mz_input()))

    @render.ui
    def rawfile_buttons_eim():
        MSframedict,precursordict,samplenames=rawfile_list()
        opts=dict()
        keys=input.rawfile_input().split("\n")
        labels=samplenames
        for x,y in zip(keys,labels):
            opts[x]=y
        return ui.input_radio_buttons("rawfile_pick_eim","Pick file to plot data for:",choices=opts,width="800px")

    @reactive.calc
    @reactive.event(input.load_eim)
    def eim_setup():
        mz=float(input.eim_mz_input())
        ppm_error=float(input.eim_ppm_input())
        rawfile=atb.TimsTOF(input.rawfile_pick_eim())

        low_mz=mz/(1+ppm_error/10**6)
        high_mz=mz*(1+ppm_error/10**6)

        eim_df=rawfile[:,:,0,low_mz: high_mz].sort_values("mobility_values")
        return eim_df

    #plot EIM for input mass
    @reactive.effect
    def _():
        @render.plot(width=input.eim_width(),height=input.eim_height())
        def eim():
            eim_df=eim_setup()
            fig,ax=plt.subplots(figsize=(10,5))
            ax.plot(eim_df["mobility_values"],eim_df["intensity_values"],linewidth=0.5)
            ax.set_xlabel("Ion Mobility ($1/K_{0}$)")
            ax.set_ylabel("Intensity")
            ax.set_title(input.rawfile_pick_eim().split("\\")[-1]+"\n"+"EIM: "+str(input.eim_mz_input()))

#endregion

# ============================================================================= Export Tables 
#region 

    #download table of peptide IDs
    @render.download(filename=lambda: f"Peptide List_{input.searchreport()[0]['name']}.csv")
    def peptidelist():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
        peptidetable=searchoutput[["PG.Genes","PG.ProteinAccessions","PG.ProteinGroups","PG.ProteinNames","EG.ModifiedPeptide"]].drop_duplicates().reset_index(drop=True)
        with io.BytesIO() as buf:
            peptidetable.to_csv(buf)
            yield buf.getvalue()

    #download table of protein ID metrics/CVs
    @render.download(filename=lambda: f"Protein CV Table_{input.searchreport()[0]['name']}.csv")
    def proteinidmetrics_download():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
        cvproteingroup=searchoutput[["R.Condition","R.Replicate","PG.ProteinGroups","PG.MS2Quantity"]].drop_duplicates().reset_index(drop=True)
        cvproteinmean=cvproteingroup.drop(columns="R.Replicate").groupby(["R.Condition","PG.ProteinGroups"]).mean().rename(columns={"PG.MS2Quantity":"Mean"})
        cvproteinstdev=cvproteingroup.drop(columns="R.Replicate").groupby(["R.Condition","PG.ProteinGroups"]).std().rename(columns={"PG.MS2Quantity":"Stdev"})
        cvproteincount=cvproteingroup.drop(columns="R.Replicate").groupby(["R.Condition","PG.ProteinGroups"]).size().reset_index(drop=True)
        cvproteintable=pd.concat([cvproteinmean,cvproteinstdev],axis=1).reindex(cvproteinmean.index)
        cvproteintable["CV"]=cvproteintable["Stdev"]/cvproteintable["Mean"]*100
        cvproteintable["# replicates observed"]=cvproteincount.tolist()
        with io.BytesIO() as buf:
            cvproteintable.to_csv(buf)
            yield buf.getvalue()
    
    #download table of precursor ID metrics/CVs
    @render.download(filename=lambda: f"Precursor CV Table_{input.searchreport()[0]['name']}.csv")
    def precursoridmetrics_download():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
        cvprecursorgroup=searchoutput[["R.Condition","R.Replicate","EG.ModifiedPeptide","FG.Charge","FG.MS2Quantity"]].drop_duplicates().reset_index(drop=True)

        cvprecursormean=cvprecursorgroup.drop(columns="R.Replicate").groupby(["R.Condition","EG.ModifiedPeptide","FG.Charge"]).mean().rename(columns={"FG.MS2Quantity":"Mean"})
        cvprecursorstdev=cvprecursorgroup.drop(columns="R.Replicate").groupby(["R.Condition","EG.ModifiedPeptide","FG.Charge"]).std().rename(columns={"FG.MS2Quantity":"Stdev"})
        cvprecursorcount=cvprecursorgroup.drop(columns="R.Replicate").groupby(["R.Condition","EG.ModifiedPeptide","FG.Charge"]).size().reset_index(drop=True)
        cvprecursortable=pd.concat([cvprecursormean,cvprecursorstdev],axis=1).reindex(cvprecursormean.index)
        cvprecursortable["CV"]=cvprecursortable["Stdev"]/cvprecursortable["Mean"]*100
        cvprecursortable["# replicates observed"]=cvprecursorcount.tolist()
        with io.BytesIO() as buf:
            cvprecursortable.to_csv(buf)
            yield buf.getvalue()
    
    #download table of MOMA precursors for a specified run
    @render.download(filename=lambda: f"MOMA Table_{input.searchreport()[0]['name']}.csv")
    def moma_download():
        #RT tolerance in %
        rttolerance=input.rttolerance()
        #MZ tolerance in m/z
        mztolerance=input.mztolerance()

        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()

        sample=input.cond_rep()

        columns=["EG.ModifiedPeptide","FG.Charge","EG.IonMobility","EG.ApexRT","FG.PrecMz"]
        df=searchoutput[searchoutput["Cond_Rep"]==sample][["EG.ModifiedPeptide","FG.Charge","EG.IonMobility","EG.ApexRT","FG.PrecMz"]].sort_values(["EG.ApexRT"]).reset_index(drop=True)
        coelutingpeptides=pd.DataFrame(columns=columns)
        for i in range(len(df)):
            if i+1 not in range(len(df)):
                break
            rtpercentdiff=(abs(df["EG.ApexRT"][i]-df["EG.ApexRT"][i+1])/df["EG.ApexRT"][i])*100
            mzdiff=abs(df["FG.PrecMz"][i]-df["FG.PrecMz"][i+1])
            if rtpercentdiff <= rttolerance and mzdiff <= mztolerance:
                coelutingpeptides.loc[len(coelutingpeptides)]=df.iloc[i].tolist()
                coelutingpeptides.loc[len(coelutingpeptides)]=df.iloc[i+1].tolist()

        #adding a column for a rough group number for each group of peptides detected
        for i in range(len(coelutingpeptides)):
            if i+1 not in range(len(coelutingpeptides)):
                break
            rtpercentdiff=(abs(coelutingpeptides["EG.ApexRT"][i]-coelutingpeptides["EG.ApexRT"][i+1])/coelutingpeptides["EG.ApexRT"][i])*100
            mzdiff=abs(coelutingpeptides["FG.PrecMz"][i]-coelutingpeptides["FG.PrecMz"][i+1])
            if rtpercentdiff <= rttolerance and mzdiff <= mztolerance:
                coelutingpeptides.loc[coelutingpeptides.index[i],"Group"]=i

        with io.BytesIO() as buf:
            coelutingpeptides.to_csv(buf,index=False)
            yield buf.getvalue()

    #download table of PTMs per precursor
    @render.download(filename=lambda: f"PTM List_{input.searchreport()[0]['name']}.csv")
    def ptmlist_download():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
        ptmdf=pd.DataFrame()
        for condition in sampleconditions:
            df=searchoutput[searchoutput["R.Condition"]==condition][["EG.ModifiedPeptide","FG.Charge"]].drop_duplicates().reset_index(drop=True)
            dfptmlist=[]
            numptms=[]
            for i in df["EG.ModifiedPeptide"]:
                foundptms=re.findall(r"[^[]*\[([^]]*)\]",i)
                dfptmlist.append(foundptms)
                numptms.append(len(foundptms))
            dfptmlist=pd.Series(dfptmlist).value_counts().to_frame().reset_index().rename(columns={"index":condition,"count":condition+"_count"})
            ptmdf=pd.concat([ptmdf,dfptmlist],axis=1)
        with io.BytesIO() as buf:
            ptmdf.to_csv(buf,index=False)
            yield buf.getvalue()

#endregion

# ============================================================================= Glycoproteomics
#region

    #generate dfs and variables for the glyco results
    @reactive.calc
    def glyco_variables():
        searchoutput=metadata_update()
        searchoutput["R.Condition"]=searchoutput["R.Condition"].apply(str)
        if "Cond_Rep" not in searchoutput.columns:
            searchoutput.insert(0,"Cond_Rep",searchoutput["R.Condition"]+"_"+searchoutput["R.Replicate"].apply(str))
        elif "Cond_Rep" in searchoutput.columns:
            searchoutput["Cond_Rep"]=searchoutput["R.Condition"]+"_"+searchoutput["R.Replicate"].apply(str)
        resultdf_glyco=pd.DataFrame()
        num_glycoproteins=[]
        num_glycopeptides=[]
        num_glycoPSMs=[]
        dict_glycoproteins=dict()
        dict_glycopeptides=dict()
        dict_glycoPSMs=dict()
        for run in searchoutput["Cond_Rep"].drop_duplicates():
            df=searchoutput[searchoutput["Cond_Rep"]==run]
            #all PSMs with a glycan q value (not used here)
            all_glycoPSM=df[df["Glycan q-value"].isnull()==False]
            #filtered PSMs with a q value cutoff (used for the dfs generated here)
            glycoPSM_QvalFilter=df[(df["Glycan q-value"].isnull()==False)&(df["Glycan q-value"]<=0.01)]
            #all unique glycopeptides (charge agnostic)
            glycopeptide=glycoPSM_QvalFilter[["EG.ModifiedPeptide","PG.ProteinNames"]].drop_duplicates()
            #all unique glycoproteins
            glycoprotein=glycoPSM_QvalFilter["PG.ProteinNames"].drop_duplicates()
            
            num_glycoproteins.append(len(glycoprotein))
            num_glycopeptides.append(len(glycopeptide))
            num_glycoPSMs.append(len(glycoPSM_QvalFilter))
            
            dict_glycoproteins[run]=glycoprotein.reset_index(drop=True)
            dict_glycopeptides[run]=glycopeptide.reset_index(drop=True)
            dict_glycoPSMs[run]=glycoPSM_QvalFilter.reset_index(drop=True)

        resultdf_glyco["Cond_Rep"]=searchoutput["Cond_Rep"].drop_duplicates().reset_index(drop=True)
        resultdf_glyco["glycoproteins"]=num_glycoproteins
        resultdf_glyco["glycopeptides"]=num_glycopeptides
        resultdf_glyco["glycoPSM"]=num_glycoPSMs

        return resultdf_glyco,dict_glycoproteins,dict_glycopeptides,dict_glycoPSMs

    #generate dfs for the glyco results
    @reactive.calc
    def glyco_dataframes():
        resultdf_glyco,dict_glycoproteins,dict_glycopeptides,dict_glycoPSMs=glyco_variables()
        glycoproteins_df=pd.DataFrame()
        glycopeptides_df=pd.DataFrame()
        glycoPSMs_df=pd.DataFrame()
        for key in dict_glycoproteins.keys():
            protein_key=pd.DataFrame({"Cond_Rep":[key]*len(dict_glycoproteins[key]),"PG.ProteinNames":dict_glycoproteins[key]})
            glycoproteins_df=pd.concat([glycoproteins_df,protein_key]).reset_index(drop=True)
            
            peptide_key=pd.DataFrame({"Cond_Rep":[key]*len(dict_glycopeptides[key])})
            peptide_key_df=pd.concat([peptide_key,dict_glycopeptides[key]],axis=1)
            glycopeptides_df=pd.concat([glycopeptides_df,peptide_key_df]).reset_index(drop=True)

            glycoPSMs_df=pd.concat([glycoPSMs_df,dict_glycoPSMs[key]]).reset_index(drop=True)
        return glycoproteins_df,glycopeptides_df,glycoPSMs_df

    #plot only glycosylated IDs
    @reactive.effect
    def _():
        @render.plot(width=input.glycoIDsplot_width(),height=input.glycoIDsplot_height())
        def glycoIDsplot():
            resultdf_glyco,dict_glycoproteins,dict_glycopeptides,dict_glycoPSMs=glyco_variables()
            color=replicatecolors()
            titlefont=input.titlefont()
            axisfont=input.axisfont()
            labelfont=input.labelfont()
            y_padding=input.ypadding()

            fig,ax=plt.subplots(ncols=3,sharex=True)
            fig.set_tight_layout(True)
            ax1=ax[0]
            ax2=ax[1]
            ax3=ax[2]

            resultdf_glyco.plot.bar(ax=ax1,x="Cond_Rep",y="glycoproteins",legend=False,width=0.8,color=color,edgecolor="k")
            ax1.bar_label(ax1.containers[0],label_type="edge",rotation=90,padding=5,fontsize=labelfont)
            ax1.set_ylim(top=max(resultdf_glyco["glycoproteins"].tolist())+y_padding*max(resultdf_glyco["glycoproteins"].tolist()))
            ax1.set_ylabel("Counts",fontsize=axisfont)
            ax1.set_xlabel("Condition",fontsize=axisfont)
            ax1.set_title("Glycoproteins",fontsize=titlefont)

            resultdf_glyco.plot.bar(ax=ax2,x="Cond_Rep",y="glycopeptides",legend=False,width=0.8,color=color,edgecolor="k")
            ax2.bar_label(ax2.containers[0],label_type="edge",rotation=90,padding=5,fontsize=labelfont)
            ax2.set_ylim(top=max(resultdf_glyco["glycopeptides"].tolist())+y_padding*max(resultdf_glyco["glycopeptides"].tolist()))
            ax2.set_xlabel("Condition",fontsize=axisfont)
            ax2.set_title("Glycopeptides",fontsize=titlefont)

            resultdf_glyco.plot.bar(ax=ax3,x="Cond_Rep",y="glycoPSM",legend=False,width=0.8,color=color,edgecolor="k")
            ax3.bar_label(ax3.containers[0],label_type="edge",rotation=90,padding=5,fontsize=labelfont)
            ax3.set_ylim(top=max(resultdf_glyco["glycoPSM"].tolist())+(y_padding+0.1)*max(resultdf_glyco["glycoPSM"].tolist()))
            ax3.set_xlabel("Condition",fontsize=axisfont)
            ax3.set_title("Glyco-PSMs\n(Qvalue<0.1)",fontsize=titlefont)

            ax1.set_axisbelow(True)
            ax1.grid(linestyle="--")
            ax2.set_axisbelow(True)
            ax2.grid(linestyle="--")
            ax3.set_axisbelow(True)
            ax3.grid(linestyle="--")

    #show data grid for glycoproteins
    @render.data_frame
    def glycoproteins_df_view():
        glycoproteins_df,glycopeptides_df,glycoPSMs_df=glyco_dataframes()
        return render.DataGrid(glycoproteins_df,editable=False,height="600px")

    #download shown data grid for glycoproteins
    @render.download(filename=lambda: f"glycoproteins_{input.searchreport()[0]['name']}.csv")
    def glycoproteins_download():
        glycoprotein_table=glycoproteins_df_view.data_view()
        with io.BytesIO() as buf:
            glycoprotein_table.to_csv(buf,index=False)
            yield buf.getvalue()

    #show data grid for glycopeptides
    @render.data_frame
    def glycopeptides_df_view():
        glycoproteins_df,glycopeptides_df,glycoPSMs_df=glyco_dataframes()
        return render.DataGrid(glycopeptides_df,editable=False,height="600px")

    #download shown data grid for glycopeptides
    @render.download(filename=lambda: f"glycopeptides_{input.searchreport()[0]['name']}.csv")
    def glycopeptides_download():
        glycopeptide_table=glycopeptides_df_view.data_view()
        with io.BytesIO() as buf:
            glycopeptide_table.to_csv(buf,index=False)
            yield buf.getvalue()

    #show data grid for glycoPSMs
    @render.data_frame
    def glycoPSMs_df_view():
        glycoproteins_df,glycopeptides_df,glycoPSMs_df=glyco_dataframes()
        return render.DataGrid(glycoPSMs_df,editable=False,height="600px")

    #download shown data grid for glyco PSMs
    @render.download(filename=lambda: f"glycoPSMs_{input.searchreport()[0]['name']}.csv")
    def glycoPSMs_download():
        glycoPSMs_table=glycoPSMs_df_view.data_view()
        with io.BytesIO() as buf:
            glycoPSMs_table.to_csv(buf,index=False)
            yield buf.getvalue()

    #generate selectize list of stripped peptide sequences
    @render.ui
    def glyco_peplist():
        glycoproteins_df,glycopeptides_df,glycoPSMs_df=glyco_dataframes()
        peplist=glycoPSMs_df["PEP.StrippedSequence"].drop_duplicates().sort_values().reset_index(drop=True).tolist()
        pep_dict=dict()
        for pep in peplist:
            pep_dict[pep]=pep
        return ui.input_selectize("glyco_peplist_pick","Pick stripped peptide sequence:",choices=pep_dict)
    
    #show glycoPSMs for selected stripped peptide sequence 
    @render.data_frame
    def selected_glyco_peplist():
        glycoproteins_df,glycopeptides_df,glycoPSMs_df=glyco_dataframes()
        selectedpep=input.glyco_peplist_pick()
        selectedpep_df=glycoPSMs_df[glycoPSMs_df["PEP.StrippedSequence"]==selectedpep]
        return render.DataGrid(selectedpep_df,editable=False,height="600px")

    #download shown table of glycoPSMs for selected stripped peptide sequence
    @render.download(filename=lambda: f"glycoPSMs_{input.glyco_peplist_pick()}.csv")
    def selected_glyco_download():
        glycoproteins_df,glycopeptides_df,glycoPSMs_df=glyco_dataframes()
        glycopep_table=selected_glyco_peplist.data_view()
        with io.BytesIO() as buf:
            glycopep_table.to_csv(buf,index=False)
            yield buf.getvalue()

    #scatterplot like the charge/PTM scatter for glycosylated precursors
    @reactive.effect
    def _():
        @render.plot(width=input.glycoscatter_width(),height=input.glycoscatter_height())
        def glycoscatter():
            searchoutput=metadata_update()

            searchoutput_nonglyco=searchoutput[searchoutput["Glycan q-value"].isnull()==True]
            searchoutput_glyco=searchoutput[searchoutput["Glycan q-value"].isnull()==False]

            titlefont=input.titlefont()
            axisfont=input.axisfont()
            legendfont=input.legendfont()

            fig,ax=plt.subplots()
            ax.scatter(x=searchoutput_nonglyco["FG.PrecMz"],y=searchoutput_nonglyco["EG.IonMobility"],s=2,label="All Other Precursors")
            ax.scatter(x=searchoutput_glyco["FG.PrecMz"],y=searchoutput_glyco["EG.IonMobility"],s=2,label="Glycosylated Precursors")
            ax.set_xlabel("m/z",fontsize=axisfont)
            ax.set_ylabel("Ion Mobility ($1/K_{0}$)",fontsize=axisfont)
            ax.legend(loc="upper left",fontsize=legendfont,markerscale=5)
            ax.set_axisbelow(True)
            ax.grid(linestyle="--")

    #generate selectize list of detected glyco mods
    @render.ui
    def glycomodlist_ui():
        glycoproteins_df,glycopeptides_df,glycoPSMs_df=glyco_dataframes()

        raw_modlist=[]
        modlist=[]
        allmods=glycoPSMs_df["Total Glycan Composition"].drop_duplicates().tolist()
        for i in range(len(allmods)):
            raw_modlist.append(allmods[i].split("%")[0])
            modstring=raw_modlist[i].replace("(","").replace(")",",").replace(", ","")
            
            modlist.append("".join(i for i in modstring if not i.isdigit()))
        set_modlist=list(set(modlist))
        unique_mods=[]
        for item in set_modlist:
            if item.count(",")>=1:
                unique_mods.append(item.split(","))
            else:
                unique_mods.append([item])
        unique_mods=list(set(list(itertools.chain(*unique_mods))))
        mods_dict=dict()
        for item in unique_mods:
            mods_dict[item]=item

        return ui.input_selectize("found_glycomods","Pick glycan mod to plot data for",choices=mods_dict)
    
    #plot ID bar graph for selected glyco mod, option to show enrichment % instead of counts
    @reactive.effect
    def _():
        @render.plot(width=input.glycomodIDsplot_width(),height=input.glycomodIDsplot_height())
        def glycomod_IDs():
            resultdf_glyco,dict_glycoproteins,dict_glycopeptides,dict_glycoPSMs=glyco_variables()
            glycoproteins_df,glycopeptides_df,glycoPSMs_df=glyco_dataframes()
            picked_mod=input.found_glycomods()

            color=replicatecolors()
            titlefont=input.titlefont()
            axisfont=input.axisfont()
            labelfont=input.labelfont()
            y_padding=input.ypadding()

            resultdf_glycomod=pd.DataFrame()

            num_glycoproteins_mod=[]
            num_glycopeptides_mod=[]
            num_glycoPSMs_mod=[]

            for run in glycoPSMs_df["Cond_Rep"].drop_duplicates():
                num_glycoproteins_mod.append(len(glycoPSMs_df[(glycoPSMs_df["Cond_Rep"]==run)&(glycoPSMs_df["Total Glycan Composition"].str.contains(picked_mod))]["PG.ProteinNames"].drop_duplicates()))
                num_glycopeptides_mod.append(len(glycoPSMs_df[(glycoPSMs_df["Cond_Rep"]==run)&(glycoPSMs_df["Total Glycan Composition"].str.contains(picked_mod))]["EG.ModifiedPeptide"].drop_duplicates()))
                num_glycoPSMs_mod.append(len(glycoPSMs_df[(glycoPSMs_df["Cond_Rep"]==run)&(glycoPSMs_df["Total Glycan Composition"].str.contains(picked_mod))]))

            resultdf_glycomod["Cond_Rep"]=glycoPSMs_df["Cond_Rep"].drop_duplicates().reset_index(drop=True)
            resultdf_glycomod["glycoproteins"]=num_glycoproteins_mod
            resultdf_glycomod["glycopeptides"]=num_glycopeptides_mod
            resultdf_glycomod["glycoPSM"]=num_glycoPSMs_mod

            if input.counts_vs_enrich()=="counts":
                plottingdf=resultdf_glycomod
            if input.counts_vs_enrich()=="enrich":
                resultdf_glyco_enrich=round(resultdf_glycomod.drop(columns=["Cond_Rep"])/resultdf_glyco.drop(columns=["Cond_Rep"])*100,1)
                resultdf_glyco_enrich["Cond_Rep"]=glycoPSMs_df["Cond_Rep"].drop_duplicates().reset_index(drop=True)
                plottingdf=resultdf_glyco_enrich

            fig,ax=plt.subplots(ncols=3,sharex=True)
            fig.set_tight_layout(True)
            ax1=ax[0]
            ax2=ax[1]
            ax3=ax[2]

            plottingdf.plot.bar(ax=ax1,x="Cond_Rep",y="glycoproteins",legend=False,width=0.8,color=color,edgecolor="k")
            ax1.bar_label(ax1.containers[0],label_type="edge",rotation=90,padding=5,fontsize=labelfont)
            ax1.set_ylim(top=max(plottingdf["glycoproteins"].tolist())+y_padding*max(plottingdf["glycoproteins"].tolist()))
            ax1.set_ylabel("Counts",fontsize=axisfont)
            ax1.set_xlabel("Condition",fontsize=axisfont)
            ax1.set_title("Glycoproteins",fontsize=titlefont)

            plottingdf.plot.bar(ax=ax2,x="Cond_Rep",y="glycopeptides",legend=False,width=0.8,color=color,edgecolor="k")
            ax2.bar_label(ax2.containers[0],label_type="edge",rotation=90,padding=5,fontsize=labelfont)
            ax2.set_ylim(top=max(plottingdf["glycopeptides"].tolist())+y_padding*max(plottingdf["glycopeptides"].tolist()))
            ax2.set_xlabel("Condition",fontsize=axisfont)
            ax2.set_title("Glycopeptides",fontsize=titlefont)

            plottingdf.plot.bar(ax=ax3,x="Cond_Rep",y="glycoPSM",legend=False,width=0.8,color=color,edgecolor="k")
            ax3.bar_label(ax3.containers[0],label_type="edge",rotation=90,padding=5,fontsize=labelfont)
            ax3.set_ylim(top=max(plottingdf["glycoPSM"].tolist())+(y_padding+0.1)*max(plottingdf["glycoPSM"].tolist()))
            ax3.set_xlabel("Condition",fontsize=axisfont)
            ax3.set_title("Glyco-PSMs\n(Qvalue<0.1)",fontsize=titlefont)

            ax1.set_axisbelow(True)
            ax1.grid(linestyle="--")
            ax2.set_axisbelow(True)
            ax2.grid(linestyle="--")
            ax3.set_axisbelow(True)
            ax3.grid(linestyle="--")


#endregion

app=App(app_ui,server)