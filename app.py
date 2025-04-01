#Changelog

# =============================================================================
# Library Imports (only necessary for launch)
# =============================================================================
#region

from shiny import App, Inputs, Outputs, Session, reactive, render, ui, module
from shinyswatch import theme
#https://rstudio.github.io/shinythemes/
from shiny.types import ImgData
from faicons import icon_svg
# #https://fontawesome.com/search?o=r&m=free

#endregion

# =============================================================================
# UI
# =============================================================================
#region

app_ui=ui.page_fluid(
    ui.panel_title("timsplot: timsTOF Proteomics Data Visualization (v.2025.04.01)"),
    ui.navset_pill_list(
        ui.nav_panel("File Import",
                     ui.card(
                         ui.card_header("Upload Search Report"),
                         ui.row(
                            ui.column(3,
                                      ui.input_radio_buttons("software","Search software:",{"spectronaut":"Spectronaut",
                                                                                            "diann":"DIA-NN (pre 2.0)",
                                                                                            "diann2.0":"DIA-NN (2.0)",
                                                                                            "fragpipe":"FragPipe",
                                                                                            "fragpipe_glyco":"FragPipe (Glyco)",
                                                                                            "glycoscape":"GlycoScape",
                                                                                            "bps_timsrescore":"tims-rescore (BPS)",
                                                                                            "bps_timsdiann":"tims-DIANN (BPS)",
                                                                                            "bps_denovo":"BPS Novor",
                                                                                            "ddalibrary":"Spectronaut Library"}),
                                      ),
                            ui.column(4,
                                      ui.input_file("searchreport","Upload search report(s):",accept=[".tsv",".zip",".parquet"],multiple=True),
                                      ui.output_ui("diann_mbr_ui"),
                                      ui.output_text("metadata_reminder")
                                      ),
                            ui.column(5,
                                      ui.p("Instructions:"),
                                      ui.p("-Note: if using the app in a browser window, zoom out to 90%,"),
                                      ui.p("-Select software used for search and upload .tsv, .zip, or .parquet file (multiple .tsv or .parquet files can be uploaded)"),
                                      ui.p("-Fill out R.Condition and R.Replicate in the metadata table as needed"),
                                      ui.p("-Select necessary switches under 'Update from Metadata Table' and click the 'Apply Changes' button"),
                                      ui.p("-Note: click on the 'Apply Changes' button after upload even if metadata table was not updated")
                                      )
                                ),
                            ),
                     ui.card(
                         ui.card_header("Update from Metadata Table"),
                         ui.row(
                             ui.column(4,
                                       ui.input_action_button("rerun_metadata","Apply Changes",width="300px",class_="btn-primary",icon=icon_svg("rotate"))
                                       ),
                             ui.column(4,
                                          ui.input_switch("condition_names","Update 'R.Condition' and 'R.Replicate' columns",width="100%"),
                                          ui.input_switch("remove","Remove selected runs")            
                                          ),
                             ui.column(4,
                                          ui.input_switch("reorder","Reorder runs"),
                                          ui.input_switch("concentration","Update 'Concentration' column")
                                )
                                ),
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
                                       ui.p("-To remove runs, add an 'x' to the 'remove' column"),
                                       ui.p("-To reorder conditions, order them numerically in the 'order' column")
                                       ),
                            ),
                         ui.row(
                             ui.column(8,
                                       ui.output_data_frame("metadata_table")
                                       ),
                             ui.column(4,
                                       ui.output_data_frame("metadata_condition_table")
                                       )
                                       )
                     ),icon=icon_svg("folder-open")
                    ),
        ui.nav_panel("Settings",
                     ui.navset_pill(
                         ui.nav_panel("Color Settings",
                                      ui.row(
                                             ui.column(4,
                                                       ui.input_radio_buttons("coloroptions","Choose coloring option for output plots:",choices={"pickrainbow":"Pick for me (rainbow)","pickmatplot":"Pick for me (matplotlib tableau)","custom":"Custom"},selected="pickmatplot"),
                                                       ui.input_text_area("customcolors","Input color names from the tables to the right, one per line (hex codes can also be used):",autoresize=True),
                                                       ui.output_text("colornote"),
                                                       ui.row(ui.column(5,
                                                                        ui.output_table("customcolors_table1")
                                                                        ),
                                                              ui.column(5,
                                                                        ui.output_table("conditioncolors"),
                                                                        ui.output_plot("customcolors_plot")
                                                                        )
                                                              )
                                                       ),
                                             ui.column(2,
                                                       ui.p("Matplotlib Tableau Colors:"),
                                                       ui.output_image("matplotcolors_image"),
                                                       #ui.output_plot("matplotlibcolors")
                                                       ),
                                             ui.column(5,
                                                       ui.p("CSS Colors:"),
                                                       ui.output_image("csscolors_image")
                                                       #ui.output_plot("csscolors")
                                                       ),
                                             ),
                                     ui.output_ui("colorplot_height")
                                     ),
                         ui.nav_panel("Control Panel",
                                      ui.row(
                                          ui.column(4,
                                                    ui.card(
                                                        ui.card_header("Plot Parameters"),
                                                        ui.input_slider("titlefont","Plot title size",min=10,max=25,value=20,step=1,ticks=True),
                                                        ui.input_slider("axisfont","Axis label size",min=10,max=25,value=15,step=1,ticks=True),
                                                        ui.input_slider("labelfont","Data label size",min=10,max=25,value=15,step=1,ticks=True),
                                                        ui.input_slider("legendfont","Legend size",min=10,max=25,value=10,step=1,ticks=True),
                                                        ui.input_slider("ypadding","y-axis padding for data labels",min=0,max=1,value=0.3,step=0.05,ticks=True),
                                                        ui.input_slider("xaxis_label_rotation","x-axis label rotation",min=0,max=90,value=90,step=5,ticks=True)
                                                        )
                                                    ),
                                          ui.column(4,
                                                    ui.card(
                                                        ui.card_header("Misc."),
                                                        ui.input_radio_buttons("peptide_grouping","Grouping key for peptide CVs",choices={"stripped":"Stripped sequence","modified":"Modified sequence"}),
                                                        ui.input_switch("dpi_switch","Change DPI to 300 for publication quality",value=False,width="400px"),
                                                        ui.p("Note: values in the width/height sliders for plots will need to be increased to accommodate the DPI change, default plotting parameters will be too small since Shiny plots based on pixels."),
                                                    )
                                                    )
                                            )
                                     ),
                         ui.nav_panel("File Stats",
                                      ui.output_table("filestats")
                                      ),
                         ui.nav_panel("Column Check",
                                      ui.output_table("column_check")
                                     ),
                         ui.nav_panel("File Preview",
                                      ui.output_data_frame("filepreview")
                                      ),
                         ui.nav_panel("Extra Colors",
                                      ui.p("Bruker Colors:"),
                                      ui.output_image("brukercolors")
                                      )
                         ),icon=icon_svg("gear")
                     ),
        ui.nav_panel("ID Counts",
                     ui.navset_pill(
                         ui.nav_panel("Counts per Condition",
                                      ui.card(
                                          ui.row(
                                              ui.input_slider("idmetrics_width","Plot width",min=100,max=7500,step=100,value=1500,ticks=True),
                                              ui.input_slider("idmetrics_height","Plot height",min=100,max=7500,step=100,value=1000,ticks=True),
                                              ui.column(6,
                                                        ui.p("Proteins: number of unique values in the ProteinGroups column"),
                                                        ui.p("Proteins with >2 Peptides: number of ProteinGroups that have more than 2 unique ModifiedPeptides"),
                                                        ui.p("Peptides: number of unique values in the ModifiedPeptide column (charge agnostic)"),
                                                        ui.p("Precursors: number of unique values between the ModifiedPeptide and Charge columns")
                                                        )
                                              )
                                              ),
                                      ui.input_selectize("idplotinput","Choose what metric to plot:",choices={"all":"All","proteins":"Proteins","proteins2pepts":"Proteins with >2 Peptides","peptides":"Peptides","precursors":"Precursors"},multiple=False,selected="all"),
                                      ui.output_plot("idmetricsplot")
                                    ),
                         ui.nav_panel("Average Counts",
                                      ui.card(
                                          ui.row(
                                              ui.input_slider("avgidmetrics_width","Plot width",min=100,max=7500,step=100,value=1500,ticks=True),
                                              ui.input_slider("avgidmetrics_height","Plot height",min=100,max=7500,step=100,value=1000,ticks=True),
                                              ui.column(6,
                                                        ui.p("Proteins: number of unique values in the ProteinGroups column"),
                                                        ui.p("Proteins with >2 Peptides: number of ProteinGroups that have more than 2 unique ModifiedPeptides"),
                                                        ui.p("Peptides: number of unique values in the ModifiedPeptide column (charge agnostic)"),
                                                        ui.p("Precursors: number of unique values between the ModifiedPeptide and Charge columns")
                                                        )
                                              )
                                              ),
                                      ui.input_selectize("avgidplotinput","Choose what metric to plot:",choices={"all":"All","proteins":"Proteins","proteins2pepts":"Proteins with >2 Peptides","peptides":"Peptides","precursors":"Precursors"},multiple=False,selected="all"),
                                      ui.output_plot("avgidmetricsplot")
                                    ),
                         ui.nav_panel("CV Plots",
                                      ui.card(
                                          ui.row(
                                              ui.input_slider("cvplot_width","Plot width",min=100,max=7500,step=100,value=1000,ticks=True),
                                              ui.input_slider("cvplot_height","Plot height",min=100,max=7500,step=100,value=500,ticks=True),
                                              ui.column(6,
                                                        ui.p("Note for Peptide CVs: Go to Settings -> Control Panel to change grouping key from stripped sequence to modified sequence (default is stripped sequence). CVs calculated from top 3 precursors for a given sequence")
                                                        )
                                              )
                                            ),
                                      ui.row(
                                          ui.column(3,
                                              ui.input_radio_buttons("proteins_precursors_cvplot","Pick which IDs to plot",choices={"Protein":"Proteins","Precursor":"Precursors","Peptide":"Peptides"}),
                                              ui.input_switch("removetop5percent","Remove top 5%"),
                                              ui.output_table("cv_table")
                                                    ),
                                          ui.column(7,
                                                    ui.output_plot("cvplot")
                                                    ),
                                          ),
                                          
                                      ),
                         ui.nav_panel("IDs with CV Cutoff",
                                      ui.card(
                                          ui.row(
                                              ui.input_slider("countscvcutoff_width","Plot width",min=100,max=7500,step=100,value=900,ticks=True),
                                              ui.input_slider("countscvcutoff_height","Plot height",min=100,max=7500,step=100,value=700,ticks=True),
                                              ui.column(6,
                                                        ui.p("Note for Peptide CVs: Go to Settings -> Control Panel to change grouping key from stripped sequence to modified sequence (default is stripped sequence). CVs calculated from top 3 precursors for a given sequence")
                                                        )
                                            )
                                          ),
                                      ui.input_radio_buttons("proteins_precursors_idcutoffplot","Pick which IDs to plot",choices={"proteins":"Proteins","precursors":"Precursors","peptides":"Peptides"}),
                                      ui.output_plot("countscvcutoff")
                                    ),
                         ui.nav_panel("UpSet Plot",
                                      ui.card(
                                          ui.row(
                                              ui.input_slider("upsetplot_width","Plot width",min=100,max=7500,step=100,value=900,ticks=True),
                                              ui.input_slider("upsetplot_height","Plot height",min=100,max=7500,step=100,value=700,ticks=True)
                                            )
                                          ),
                                      ui.row(
                                          ui.column(3,
                                                    ui.input_radio_buttons("upset_condition_or_run","Pick how to plot UpSet plot:",choices={"condition":"All conditions","specific_condition":"By specific condition","individual":"All runs"}),
                                                    ),
                                          ui.column(3,
                                                    ui.input_selectize("protein_precursor_pick","Pick which IDs to plot",choices={"Protein":"Protein","Peptide":"Peptide","Precursor":"Precursor"}),
                                                    ),
                                          ui.column(3,
                                                    ui.output_ui("specific_condition_ui")
                                                    )
                                          ),
                                      ui.row(
                                          ui.column(3,
                                                    ui.input_radio_buttons("upsetfilter","Filtering option:",choices={"nofilter":"No filtering","1run":"IDs in only 1 run/replicate","n-1runs":"IDs in n-1 runs/replicates"})
                                                    ),
                                          ui.column(6,
                                                    ui.output_data_frame("upsetplot_counts")
                                                    )
                                          ),
                                      ui.output_plot("upsetplot")
                                      ),
                         ui.nav_panel("UpSet Plot (stats)",
                                      ui.card(
                                          ui.row(
                                              ui.input_slider("upsetplotstats_width","Plot width",min=100,max=7500,step=100,value=1000,ticks=True),
                                              ui.input_slider("upsetplotstats_height","Plot height",min=100,max=7500,step=100,value=500,ticks=True),
                                            )
                                          ),
                                      ui.row(
                                          ui.input_radio_buttons("upsetplotstats_whattoplot","Choose what to show for single-hit IDs:",choices={"individual":"From entire result file",
                                                                                                                                                "condition":"Specific condition in entire result file",
                                                                                                                                                "specific_condition":"From specific condition"},width="350px"),
                                          ui.output_ui("upsetplotstats_conditionlist_ui"),                                       
                                          ),
                                      ui.row(
                                          ui.input_radio_buttons("upsetplotstats_peptide_precursor","ID type to plot:",choices={"Peptide":"Peptide","Precursor":"Precursor"}),
                                          ui.input_radio_buttons("upsetplotstats_plottype","Choose how to plot:",choices={"scatter":"Scatterplot","2dhist":"2-D Histogram"}),
                                          ),
                                      ui.output_plot("upsetplotstats_singlehitIDplot"),
                                      ),
                         ui.nav_panel("Protein/Peptide Signal Tracker",
                                      ui.card(
                                          ui.row(
                                              ui.input_slider("tracker_width","Plot width",min=100,max=7500,step=100,value=900,ticks=True),
                                              ui.input_slider("tracker_height","Plot height",min=100,max=7500,step=100,value=700,ticks=True),
                                              ui.column(6,
                                                        ui.p("If no peptide is selected, protein signal across runs is shown")
                                                        )
                                            )
                                          ),
                                      ui.row(
                                          ui.column(6,
                                                    ui.output_data_frame("protein_df"),
                                                    ui.output_data_frame("pickedprotein_df")
                                            ),
                                          ui.column(6,
                                                    ui.output_plot("tracker_plot")
                                            )
                                          ),
                                      ),
                        ),icon=icon_svg("chart-simple")
                     ),
        ui.nav_panel("Metrics",
                     ui.navset_pill(
                         ui.nav_panel("Charge State",
                                      ui.card(
                                          ui.row(
                                              ui.input_slider("chargestate_width","Plot width",min=100,max=7500,step=100,value=1000,ticks=True),
                                              ui.input_slider("chargestate_height","Plot height",min=100,max=7500,step=100,value=500,ticks=True),
                                          ui.column(6,
                                                    ui.p("Charge State: calculates the frequencies of charge states from the unique entries between ModifiedPeptide and Charge columns")
                                                    )
                                            )
                                          ),
                                      ui.input_switch("chargestate_stacked","Show as stacked bar graphs"),
                                      ui.input_radio_buttons("chargestate_condition_or_run","Plot by condition or by individual run?",choices={"condition":"Condition","individual":"Individual Run"}),
                                      ui.output_plot("chargestateplot")
                                      ),
                         ui.nav_panel("Peptide Length",
                                      ui.card(
                                          ui.row(
                                              ui.input_slider("peptidelength_width","Plot width",min=100,max=7500,step=100,value=1000,ticks=True),
                                              ui.input_slider("peptidelength_height","Plot height",min=100,max=7500,step=100,value=500,ticks=True),
                                          ui.column(6,
                                                    ui.p("Peptide Length: calculates the lengths of all unique stripped peptide sequences")
                                                    )
                                            )
                                          ),
                                      ui.row(
                                          ui.column(4,
                                                    ui.input_radio_buttons("peptidelengths_condition_or_run","Plot by condition or by individual run?",choices={"condition":"Condition","individual":"Individual Run"}),
                                                    ui.input_radio_buttons("peplengthinput","Line plot or bar plot?",choices={"lineplot":"line plot","barplot":"bar plot"})
                                                    ),
                                          ui.output_ui("lengthmark_ui"),
                                          ),
                                      ui.output_plot("peptidelengthplot")
                                      ),
                         ui.nav_panel("Peptides per Protein",
                                      ui.card(
                                          ui.row(
                                              ui.input_slider("pepsperprotein_width","Plot width",min=100,max=7500,step=100,value=1000,ticks=True),
                                              ui.input_slider("pepsperprotein_height","Plot height",min=100,max=7500,step=100,value=500,ticks=True),
                                          ui.column(6,
                                                    ui.p("Peptides per Protein: counts the number of unique ModifiedPeptides for each ProteinGroup")
                                                    )
                                            )
                                          ),
                                      ui.row(
                                          ui.column(4,
                                                    ui.input_radio_buttons("pepsperprotein_condition_or_run","Plot by condition or by individual run?",choices={"condition":"Condition","individual":"Individual Run"}),
                                                    ui.input_radio_buttons("pepsperproteininput","Line plot or bar plot?",choices={"lineplot":"line plot","barplot":"bar plot"})
                                                    ),
                                          ui.column(4,
                                                    ui.input_slider("pepsperprotein_xrange","X-axis high bound",min=0,max=200,value=50,step=5,ticks=True)
                                                    )
                                            ),
                                      ui.output_plot("pepsperproteinplot")
                                      ),
                         ui.nav_panel("Dynamic Range",
                                      ui.card(
                                          ui.row(
                                              ui.input_slider("dynamicrange_width","Plot width",min=100,max=7500,step=100,value=500,ticks=True),
                                              ui.input_slider("dynamicrange_height","Plot height",min=100,max=7500,step=100,value=700,ticks=True),
                                            )
                                          ),
                                      ui.row(
                                          ui.column(5,
                                                    ui.output_ui("sampleconditions_ui"),
                                                    ui.input_selectize("meanmedian","Mean or median",choices={"mean":"mean","median":"median"}),
                                                    ui.input_numeric("top_n","Input top N proteins to display:",value=25,min=5,step=5),
                                                    ui.output_data_frame("dynamicrange_proteinrank")
                                                    ),
                                          ui.column(7,
                                                    ui.output_plot("dynamicrangeplot")
                                                    )
                                            ),
                                      ),
                         ui.nav_panel("Mass Accuracy",
                                      ui.card(
                                          ui.row(
                                              ui.input_slider("massaccuracy_width","Plot width",min=100,max=7500,step=100,value=1000,ticks=True),
                                              ui.input_slider("massaccuracy_height","Plot height",min=100,max=7500,step=100,value=500,ticks=True),
                                          )
                                      ),
                                      ui.row(
                                          ui.column(3,
                                                    ui.input_radio_buttons("massaccuracy_violin_hist","Plot as a violin plot or histogram?",choices={"violin":"Violin Plot","histogram":"Histogram"})
                                                    ),
                                          ui.column(4,
                                                    ui.output_ui("massaccuracy_bins_ui")
                                                    ),
                                      ),
                                      ui.output_plot("massaccuracy_plot")
                                      ),
                         ui.nav_panel("Data Completeness",
                                      ui.card(
                                          ui.row(
                                              ui.input_slider("datacompleteness_width","Plot width",min=100,max=7500,step=100,value=1000,ticks=True),
                                              ui.input_slider("datacompleteness_height","Plot height",min=100,max=7500,step=100,value=500,ticks=True),
                                          ui.column(6,
                                                    ui.p("Data Completeness: calculates how many runs each unique protein or stripped peptide is detected in")
                                                    )
                                            )
                                        ),
                                      ui.input_radio_buttons("protein_peptide","Pick what metric to plot:",choices={"proteins":"Proteins","peptides":"Modified Peptides","strippedpeptides":"Stripped Peptides"}),
                                      ui.input_switch("datacompleteness_sampleconditions_switch","Plot for specific condition?",value=False),
                                      ui.output_ui("datacompleteness_sampleconditions_ui"),
                                      ui.output_plot("datacompletenessplot")
                                      ),
                         ui.nav_panel("Peak Width",
                                      ui.card(
                                          ui.row(
                                              ui.input_slider("peakwidth_width","Plot width",min=100,max=7500,step=100,value=1000,ticks=True),
                                              ui.input_slider("peakwidth_height","Plot height",min=100,max=7500,step=100,value=500,ticks=True)
                                          )
                                        ),
                                      ui.row(
                                          ui.column(5,
                                                    ui.input_switch("peakwidth_removetop5percent","Remove top 5%"),
                                                    ui.output_table("peakwidth_table"),
                                                    ),
                                          ui.column(7,
                                                    ui.output_plot("peakwidthplot")
                                                    )
                                            ),              
                                      ),
                         ui.nav_panel("Missed Cleavages",
                                      ui.card(
                                          ui.row(
                                              ui.input_slider("missedcleavages_width","Plot width",min=100,max=7500,step=100,value=1000,ticks=True),
                                              ui.input_slider("missedcleavages_height","Plot height",min=100,max=7500,step=100,value=600,ticks=True)
                                          )
                                        ),
                                      ui.input_slider("missedcleavages_barwidth","Bar width",min=0.1,max=1,step=0.05,value=0.25,ticks=True),
                                      ui.input_radio_buttons("enzyme_rules","Enzyme cleavage rules",choices={"trypsin":"Trypsin (K/R)"}),
                                      ui.output_plot("missedcleavages_plot")
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
                                              ui.input_slider("ptmidmetrics_width","Plot width",min=100,max=7500,step=100,value=1500,ticks=True),
                                              ui.input_slider("ptmidmetrics_height","Plot height",min=100,max=7500,step=100,value=1000,ticks=True),
                                          ui.column(6,
                                                    ui.p("Count logic is the same here as Counts per Condition, but with a condition that the ModifiedPeptide contains the specified PTM")
                                                    )
                                            )
                                          ),
                                      ui.row(
                                          ui.input_selectize("ptmidplotinput","Choose what metric to plot:",choices={"all":"All","proteins":"Proteins","proteins2pepts":"Proteins with >2 Peptides","peptides":"Peptides","precursors":"Precursors"},multiple=False,selected="all"),
                                          ui.input_radio_buttons("ptm_counts_vs_enrich","Show counts or % of IDs?",choices={"counts":"Counts","percent":"% of IDs (enrichment)"})
                                          ),
                                      ui.output_plot("ptmidmetricsplot")
                                      ),
                         ui.nav_panel("CV Plots",
                                      ui.card(
                                          ui.row(
                                              ui.input_slider("ptmcvplot_width","Plot width",min=100,max=7500,step=100,value=1000,ticks=True),
                                              ui.input_slider("ptmcvplot_height","Plot height",min=100,max=7500,step=100,value=500,ticks=True)
                                            )
                                        ),
                                      ui.row(
                                          ui.input_radio_buttons("ptm_proteins_precursors","Pick which IDs to plot",choices={"Protein":"Protein","Precursor":"Precursor","Peptide":"Peptide"}),
                                          ui.input_switch("ptm_removetop5percent","Remove top 5%"),
                                          ui.output_table("ptm_cvtable")
                                          ),
                                      ui.output_plot("ptm_cvplot")
                                      ),
                         ui.nav_panel("Mass Accuracy",
                                      ui.card(
                                          ui.row(
                                              ui.input_slider("ptm_massaccuracy_width","Plot width",min=100,max=7500,step=100,value=1000,ticks=True),
                                              ui.input_slider("ptm_massaccuracy_height","Plot height",min=100,max=7500,step=100,value=500,ticks=True),
                                          )
                                      ),
                                      ui.row(
                                          ui.column(3,
                                                    ui.input_radio_buttons("ptm_massaccuracy_violin_hist","Plot as a violin plot or histogram?",choices={"violin":"Violin Plot","histogram":"Histogram"})
                                                    ),
                                          ui.column(4,
                                                    ui.output_ui("ptm_massaccuracy_bins_ui")
                                                    ),
                                      ),
                                      ui.output_plot("ptm_massaccuracy_plot")
                                      ),
                         ui.nav_panel("PTMs per Precursor",
                                      ui.card(
                                          ui.row(
                                              ui.input_slider("ptmsperprecursor_width","Plot width",min=100,max=7500,step=100,value=1000,ticks=True),
                                              ui.input_slider("ptmsperprecursor_height","Plot height",min=100,max=7500,step=100,value=600,ticks=True),
                                          ui.column(6,
                                                    ui.p("PTMs per Precursor: counts the number of PTMs in each ModifiedPeptide value. Agnostic to PTM identity, a more detailed list of the PTM combinations can be exported in the Export Tables section")
                                                    )
                                            )
                                          ),
                                      ui.input_slider("barwidth","Bar width",min=0.1,max=1,step=0.05,value=0.25,ticks=True),
                                      ui.output_plot("ptmsperprecursor")
                                      )
                            ),icon=icon_svg("magnifying-glass")
                     ),
        ui.nav_panel("Heatmaps",
                     ui.navset_pill(
                        ui.nav_panel("RT, m/z, IM Heatmaps",
                                     ui.card(
                                         ui.row(
                                            ui.input_slider("heatmap_width","Plot width",min=100,max=7500,step=100,value=1400,ticks=True),
                                            ui.input_slider("heatmap_height","Plot height",min=100,max=7500,step=100,value=1000,ticks=True)
                                            )
                                        ),
                                     ui.row(
                                         ui.input_slider("heatmap_numbins","Number of bins:",min=10,max=250,value=100,step=10,ticks=True),
                                         ui.input_selectize("heatmap_cmap","Heatmap Color:",choices={"default":"White_Blue_Red","viridis":"Viridis","plasma":"Plasma","inferno":"Inferno","magma":"Magma","cividis":"Cividis"}),
                                         ui.input_radio_buttons("conditiontype","Plot by individual replicate or by condition:",choices={"replicate":"By replicate","condition":"By condition"},width="350px"),
                                         ui.output_ui("cond_rep_list_heatmap"),
                                        ),
                                     ui.output_plot("replicate_heatmap")
                                     ),
                        ui.nav_panel("Charge/PTM Precursor Heatmap",
                                     ui.card(
                                         ui.row(
                                            ui.input_slider("chargeptmheatmap_width","Plot width",min=100,max=7500,step=100,value=1000,ticks=True),
                                            ui.input_slider("chargeptmheatmap_height","Plot height",min=100,max=7500,step=100,value=500,ticks=True)
                                            )
                                        ),
                                     ui.row(
                                         ui.column(3,
                                                   ui.download_button("diawindows_template","Download DIA Window Template",width="300px",icon=icon_svg("file-arrow-down")),
                                                   ui.input_file("diawindow_upload","Upload DIA windows as a .csv:"),
                                                   ui.input_radio_buttons("windows_choice","Choose DIA windows to overlay:",choices={"imported":"Imported DIA windows","lubeck":"Lubeck DIA","phospho":"Phospho DIA","bremen":"Bremen DIA","None":"None"},selected="None"),
                                                   ui.input_selectize("chargeptmheatmap_cmap","Heatmap Color:",choices={"default":"White_Blue_Red","viridis":"Viridis","plasma":"Plasma","inferno":"Inferno","magma":"Magma","cividis":"Cividis"}),
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
                                            ui.input_slider("chargeptmscatter_width","Plot width",min=100,max=7500,step=100,value=800,ticks=True),
                                            ui.input_slider("chargeptmscatter_height","Plot height",min=100,max=7500,step=100,value=600,ticks=True)
                                            )
                                        ),
                                     ui.row(
                                         ui.column(3,
                                                   ui.output_ui("chargeptmscatter_cond_rep"),
                                                   ui.output_ui("ptm_chargeptmscatter_ui"),
                                                   ui.output_ui("chargestates_chargeptmscatter_ui"),
                                                   ui.output_table("chargeptmscatter_table")
                                                   ),
                                         ui.column(8,
                                                   ui.output_plot("chargeptmscatter")
                                                  )
                                            ),
                                     ),
                        ui.nav_panel("#IDs vs RT",
                                     ui.card(
                                         ui.row(
                                            ui.input_slider("idsvsrt_width","Plot width",min=100,max=7500,step=100,value=1000,ticks=True),
                                            ui.input_slider("idsvsrt_height","Plot height",min=100,max=7500,step=100,value=500,ticks=True),
                                            ui.column(6,
                                                    ui.p("#IDs vs RT: generates a histogram based on the ApexRT values in each run. An estimate of the maximum retention time is used to determine the timespan of each histogram bin"),
                                                    ui.p("Changing the bin size changes the RT range over which IDs are grouped in the histogram")
                                                    )
                                            )
                                        ),
                                     ui.row(
                                        ui.column(3,ui.output_ui("ids_vs_rt_checkbox")),
                                        ui.column(8,ui.output_ui("binslider_ui"),ui.output_plot("ids_vs_rt")))
                                     ),
                        ui.nav_panel("Venn Diagram",
                                     ui.card(
                                         ui.row(
                                            ui.input_slider("venn_width","Plot width",min=100,max=7500,step=100,value=1000,ticks=True),
                                            ui.input_slider("venn_height","Plot height",min=100,max=7500,step=100,value=500,ticks=True)
                                            )
                                        ),
                                     ui.row(
                                         ui.column(4,
                                                   ui.input_radio_buttons("venn_numcircles","Pick number of runs to compare:",choices={"2":"2","3":"3"}),
                                                   ui.input_radio_buttons("venn_conditionorrun","Plot by condition or individual run?",choices={"condition":"Condition","individual":"Individual Run"}),
                                                   ui.input_radio_buttons("venn_plotproperty","Metric to compare:",choices={"proteingroups":"Protein Groups",
                                                                                                                            "peptides":"Peptides",
                                                                                                                            "precursors":"Precursors",
                                                                                                                            "peptides_stripped":"Stripped Peptides",
                                                                                                                            }),
                                                   ui.output_ui("venn_ptm_ui"),
                                                   ui.output_ui("venn_ptmlist_ui"),
                                                   ui.output_ui("venn_specific_length_ui"),
                                                   ui.output_ui("venn_peplength_ui"),
                                                   ui.output_ui("peptidecore_ui")
                                                   ),
                                         ui.column(4,
                                                   ui.output_ui("venn_run1_ui"),
                                                   ui.output_ui("venn_run2_ui"),
                                                   ui.output_ui("venn_run3_ui"),
                                                   ui.download_button("venn_download","Download Venn list",width="300px",icon=icon_svg("file-arrow-down"))
                                                   )
                                     ),
                                     ui.output_plot("venn_plot")
                                     ),
                        ui.nav_panel("Histogram",
                                     ui.card(
                                         ui.row(
                                            ui.input_slider("histogram_width","Plot width",min=100,max=7500,step=100,value=800,ticks=True),
                                            ui.input_slider("histogram_height","Plot height",min=100,max=7500,step=100,value=600,ticks=True)
                                            )
                                        ),
                                     ui.row(
                                         ui.column(4,
                                                   ui.output_ui("histogram_cond_rep_list"),
                                                   ui.input_radio_buttons("histogram_pick","Pick property to plot:",choices={"ionmobility":"Ion Mobility",
                                                                                                                             "precursormz":"Precursor m/z",
                                                                                                                             "precursorintensity":"Precursor Intensity",
                                                                                                                             "proteinintensity":"Protein Intensity"}),
                                                   ui.input_slider("histogram_numbins","Number of bins:",min=10,max=250,value=100,step=10,ticks=True),
                                                   ),
                                         ui.column(8,
                                                   ui.output_plot("histogram_plot")
                                                   )
                                            )
                                    )
                        ),icon=icon_svg("chart-area")
                     ),
        ui.nav_panel("Statistics",
                     ui.navset_pill(
                         ui.nav_panel("Volcano Plot",
                                      ui.card(
                                          ui.row(
                                            ui.input_slider("volcano_width","Plot width",min=100,max=7500,step=100,value=1000,ticks=True),
                                            ui.input_slider("volcano_height","Plot height",min=100,max=7500,step=100,value=500,ticks=True)
                                          )
                                          ),
                                          ui.row(
                                              ui.column(4,
                                                        ui.output_ui("volcano_condition1"),
                                                        ui.output_ui("volcano_condition2"),
                                                        ui.download_button("volcano_download","Download protein table",width="300px",icon=icon_svg("file-arrow-down")),
                                                        ui.input_switch("show_labels","Show protein labels"),
                                                        ui.input_numeric("label_fontsize","Label size",value=4),
                                                        ),
                                              ui.column(4,
                                                        ui.input_slider("volcano_pvalue","log10 pvalue cutoff",min=0.5,max=5.0,value=1.0,step=0.1,ticks=True),
                                                        ui.input_slider("volcano_foldchange","log2 fold change cutoff (absolute value)",min=0.1,max=2.0,value=0.5,step=0.1,ticks=True),
                                                        ui.input_switch("volcano_h_v_lines","Show lines for pvalue and fold change cutoffs")
                                                        ),
                                              ui.column(4,
                                                        ui.input_slider("volcano_xplotrange","Plot x Range",min=-10,max=10,value=[-2,2],step=0.5,ticks=True,drag_range=True),
                                                        ui.input_slider("volcano_yplotrange","Plot y Range",min=-10,max=10,value=[0,2],step=0.5,ticks=True,drag_range=True),
                                                        ui.input_switch("volcano_plotrange_switch","Use sliders for axis ranges")
                                                        ),
                                          ),
                                          ui.output_plot("volcanoplot")
                                      ),
                         ui.nav_panel("Volcano Plot - Feature Plot",
                                      ui.card(
                                          ui.row(
                                            ui.input_slider("volcano_feature_width","Plot width",min=100,max=7500,step=100,value=800,ticks=True),
                                            ui.input_slider("volcano_feature_height","Plot height",min=100,max=7500,step=100,value=600,ticks=True),
                                            ui.column(6,
                                                      ui.p("Select multiple rows in the data table by holding Control and clicking on rows"),
                                                      ui.p("Control and Test conditions specified in the Volcano Plot tab")
                                                      )
                                          )
                                          ),
                                      ui.row(
                                          ui.column(6,
                                                    ui.output_data_frame("feature_table")
                                                    ),
                                          ui.column(6,
                                                    ui.output_plot("feature_plot")                                              
                                                    )
                                            )
                                      ),
                         ui.nav_panel("Volcano Plot - Up/Down Regulation",
                                      ui.card(
                                          ui.row(
                                            ui.input_slider("volcano_regulation_width","Plot width",min=100,max=7500,step=100,value=800,ticks=True),
                                            ui.input_slider("volcano_regulation_height","Plot height",min=100,max=7500,step=100,value=600,ticks=True)
                                          )
                                          ),
                                      ui.input_selectize("regulation_upordown","Show up- or down-regulated proteins?",choices={"up":"Upregulated","down":"Downregulated"}),
                                      ui.input_slider("regulation_topN","Pick top N proteins to show:",min=5,max=50,value=30,step=5,ticks=True),
                                      ui.output_plot("volcano_updownregulation_plot")
                                      ),
                         ui.nav_panel("PCA",
                                    ui.card(
                                        ui.row(
                                            ui.input_slider("pca_width","Plot width",min=100,max=7500,step=100,value=1000,ticks=True),
                                            ui.input_slider("pca_height","Plot height",min=100,max=7500,step=100,value=500,ticks=True)
                                            )
                                          ),
                                      ui.output_plot("pca_plot")
                                      )
                      ),icon=icon_svg("network-wired")
                     ),       
        ui.nav_panel("Immunopeptidomics",
                     ui.navset_pill(
                         ui.nav_panel("Sequence Motifs",
                                      ui.card(
                                          ui.row(
                                            ui.input_slider("seqmotif_width","Plot width",min=100,max=7500,step=100,value=1000,ticks=True),
                                            ui.input_slider("seqmotif_height","Plot height",min=100,max=7500,step=100,value=500,ticks=True)
                                          )
                                          ),
                                      ui.row(
                                          ui.column(3,
                                                    ui.input_radio_buttons("seqmotif_plottype","Pick kind of matrix to plot:",choices={"information":"Information","counts":"Counts"}),
                                                    ui.input_slider("seqmotif_peplengths","Pick peptide length to plot:",min=7,max=25,value=9,step=1,ticks=True),
                                                    ui.output_ui("seqmotif_run_ui"),
                                                    ),
                                          ui.column(8,
                                                    ui.output_plot("seqmotif_plot")
                                                    )
                                      )
                                      ),
                         ui.nav_panel("Charge States (Bar)",
                                      ui.card(
                                          ui.row(
                                            ui.input_slider("charge_barchart_width","Plot width",min=100,max=7500,step=100,value=1000,ticks=True),
                                            ui.input_slider("charge_barchart_height","Plot height",min=100,max=7500,step=100,value=500,ticks=True)
                                          )
                                          ),
                                      ui.row(
                                          ui.column(4,
                                                    ui.input_radio_buttons("chargestate_bar_condition_or_run","Plot by condition or by individual run?",choices={"condition":"Condition","individual":"Individual Run"})
                                                    ),
                                          ui.column(4,
                                                    ui.input_switch("chargestate_charges_usepickedcharges","Use picked charges"),
                                                    ui.output_ui("chargestate_charges_ui"))
                                            ),
                                      ui.output_plot("charge_barchart")
                                      ),
                         ui.nav_panel("Charge States (Stacked)",
                                      ui.card(
                                          ui.row(
                                            ui.input_slider("charge_stackedbarchart_width","Plot width",min=100,max=7500,step=100,value=1000,ticks=True),
                                            ui.input_slider("charge_stackedbarchart_height","Plot height",min=100,max=7500,step=100,value=500,ticks=True)
                                          )
                                          ),
                                      ui.row(
                                          ui.input_radio_buttons("chargestate_stacked_condition_or_run","Plot by condition or by individual run?",choices={"condition":"Condition","individual":"Individual Run"}),
                                          ui.output_data_frame("charge_stacked_table")
                                          ),
                                      ui.output_plot("charge_stacked_barchart")
                                      ),
                         ui.nav_panel("Charge States per Peptide Length",
                                      ui.card(
                                          ui.row(
                                            ui.input_slider("chargestate_peplength_width","Plot width",min=100,max=7500,step=100,value=1000,ticks=True),
                                            ui.input_slider("chargestate_peplength_height","Plot height",min=100,max=7500,step=100,value=500,ticks=True)
                                          )
                                          ),
                                      ui.row(
                                          ui.column(4,
                                                    ui.input_radio_buttons("chargestate_peplength_condition_or_run","Plot by condition or by individual run?",choices={"condition":"Condition","individual":"Individual Run"}),
                                                    ui.output_ui("chargestate_peplength_plotrange_ui")
                                                    ),
                                          ui.column(4,
                                                    ui.input_switch("usepickedcharges","Use picked charges"),
                                                    ui.output_ui("chargestate_peplength_charges_ui")
                                                    )
                                          ),
                                      ui.output_plot("chargestate_peplength")
                                      ),
                     ),icon=icon_svg("vial-virus")
                     ),
        ui.nav_panel("Mixed Proteome",
                      ui.navset_pill(
                             ui.nav_panel("Info",
                                          ui.output_data_frame("organismtable"),
                                          ui.input_radio_buttons("coloroptions_sumint","Use matplotlib tableau colors or blues/grays?",choices={"matplot":"matplotlib tableau","bluegray":"blues/grays"})
                                          ),
                             ui.nav_panel("Counts per Organism",
                                          ui.card(
                                              ui.row(
                                                  ui.input_slider("countsperorganism_width","Plot width",min=100,max=7500,step=100,value=1000,ticks=True),
                                                  ui.input_slider("countsperorganism_height","Plot height",min=100,max=7500,step=100,value=700,ticks=True)
                                                )
                                            ),
                                          ui.input_selectize("countsplotinput","Choose what metric to plot:",choices={"proteins":"Proteins","peptides":"Peptides","precursors":"Precursors"},multiple=False),
                                          ui.output_plot("countsperorganism")
                                          ),
                             ui.nav_panel("Summed Intensities",
                                          ui.card(
                                              ui.row(
                                                  ui.input_slider("summedintensities_width","Plot width",min=100,max=7500,step=100,value=1000,ticks=True),
                                                  ui.input_slider("summedintensities_height","Plot height",min=100,max=7500,step=100,value=700,ticks=True)
                                              )
                                            ),
                                          ui.output_plot("summedintensities")
                                          ),
                             ui.nav_panel("Quant Ratios",
                                          ui.card(
                                              ui.row(
                                                  ui.input_slider("quantratios_width","Plot width",min=100,max=7500,step=100,value=1200,ticks=True),
                                                  ui.input_slider("quantratios_height","Plot height",min=100,max=7500,step=100,value=600,ticks=True),
                                                  ui.column(6,
                                                      ui.p("Experimental ratios will be shown as a dashed line and theoretical ratios will be shown as a solid line")
                                                      )
                                              )
                                            ),
                                          ui.row(
                                              ui.column(3,
                                                        ui.output_ui("referencecondition"),
                                                        ui.output_ui("testcondition"),
                                                        ui.input_radio_buttons("quantratios_mean_median","Plot using mean or median quant?",choices={"mean":"mean","median":"median"}),
                                                        ui.row(
                                                            ui.column(6,
                                                                      ui.input_radio_buttons("x_log_scale","x-axis Log Scale",choices=["log2","log10"]),
                                                                     ),
                                                            ui.column(6,
                                                                      ui.input_radio_buttons("y_log_scale","y-axis Log Scale",choices=["log2","log10"]),  
                                                                     )
                                                            )
                                                        ),
                                              ui.column(3,
                                                        ui.input_slider("plotrange","Plot Range",min=-10,max=10,value=[-2,2],step=0.5,ticks=True,width="400px",drag_range=True),
                                                        ui.input_switch("plotrange_switch","Use slider for y-axis range"),
                                                        ui.input_slider("cvcutofflevel","CV Cutoff Level (%)",min=10,max=50,value=20,step=10,ticks=True,width="400px"),
                                                        ui.input_switch("cvcutoff_switch","Include CV cutoff?")
                                                        ),
                                              ui.column(6,
                                                        ui.output_table("quantratios_table"),
                                                        )
                                                        ),
                                          ui.output_plot("quantratios")
                                          )
                            ),icon=icon_svg("flask")
                      ),
        ui.nav_panel("PRM",
                     ui.navset_pill(
                        ui.nav_panel("PRM List",
                                     ui.download_button("prm_template","Download PRM Template",width="300px",icon=icon_svg("file-arrow-down")),
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
                                            ui.input_slider("prmpeptracker_width","Plot width",min=100,max=7500,step=100,value=1000,ticks=True),
                                            ui.input_slider("prmpeptracker_height","Plot height",min=100,max=7500,step=100,value=700,ticks=True)
                                        )
                                     ),
                                     ui.output_ui("prmpeptracker_pick"),
                                     ui.output_plot("prmpeptracker_plot")
                                     ),
                        ui.nav_panel("PRM Peptides - Intensity Across Runs",
                                     ui.card(
                                        ui.row(
                                            ui.input_slider("prmpepintensity_width","Plot width",min=100,max=7500,step=100,value=1000,ticks=True),
                                            ui.input_slider("prmpepintensity_height","Plot height",min=100,max=7500,step=100,value=700,ticks=True)
                                        )
                                     ),
                                     ui.output_plot("prmpepintensity_plot"),
                                     ),
                        ),icon=icon_svg("crosshairs")
                    ),
        ui.nav_panel("Dilution Series",
                     ui.navset_pill(
                         ui.nav_panel("Dilution Ratios",
                                      ui.card(
                                          ui.row(
                                            ui.input_slider("dilutionseries_width","Plot width",min=100,max=7500,step=100,value=1000,ticks=True),
                                            ui.input_slider("dilutionseries_height","Plot height",min=100,max=7500,step=100,value=700,ticks=True)
                                            )
                                            ),
                                      ui.output_ui("normalizingcondition"),
                                      ui.output_plot("dilutionseries_plot")
                                    )
                     ),icon=icon_svg("vials")
                    ),
        ui.nav_panel("Glycoproteomics",
                     ui.navset_pill(
                         ui.nav_panel("Glyco ID Metrics",
                                      ui.card(
                                          ui.row(
                                              ui.input_slider("glycoIDsplot_width","Plot width",min=100,max=7500,step=100,value=1000,ticks=True),
                                              ui.input_slider("glycoIDsplot_height","Plot height",min=100,max=7500,step=100,value=500,ticks=True)
                                            )
                                          ),
                                      ui.output_plot("glycoIDsplot")
                                      ),
                         ui.nav_panel("Venn Diagram",
                                     ui.card(
                                         ui.row(
                                            ui.input_slider("glyco_venn_width","Plot width",min=100,max=7500,step=100,value=1000,ticks=True),
                                            ui.input_slider("glyco_venn_height","Plot height",min=100,max=7500,step=100,value=500,ticks=True)
                                            )
                                        ),
                                     ui.row(
                                         ui.column(4,
                                                   ui.input_radio_buttons("glyco_venn_numcircles","Pick number of runs to compare:",choices={"2":"2","3":"3"}),
                                                   ui.input_radio_buttons("glyco_venn_conditionorrun","Plot by condition or individual run?",choices={"condition":"Condition","individual":"Individual Run"}),
                                                   ui.input_radio_buttons("glyco_venn_plotproperty","Metric to compare:",choices={"glycoproteins":"Glycoproteins","glycopeptides":"Glycopeptides","glycoPSMs":"GlycoPSMs"}),
                                                   ),
                                         ui.column(4,
                                                   ui.output_ui("glyco_venn_run1_ui"),
                                                   ui.output_ui("glyco_venn_run2_ui"),
                                                   ui.output_ui("glyco_venn_run3_ui"),
                                                   ui.download_button("glyco_venn_download","Download Venn list",width="300px",icon=icon_svg("file-arrow-down"))
                                                   )
                                            ),
                                     ui.output_plot("glyco_venn_plot")
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
                                              ui.input_slider("glycomodIDsplot_width","Plot width",min=100,max=7500,step=100,value=1000,ticks=True),
                                              ui.input_slider("glycomodIDsplot_height","Plot height",min=100,max=7500,step=100,value=500,ticks=True)
                                            )
                                          ),
                                      ui.row(
                                          ui.output_ui("glycomodlist_ui"),
                                          ui.input_radio_buttons("counts_vs_enrich","Show counts or % of IDs?",choices={"counts":"Counts","percent":"% of IDs (enrichment)"}),
                                          ui.output_ui("high_mannose_ui")
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
                                              ui.input_slider("glycoscatter_width","Plot width",min=100,max=7500,step=100,value=1000,ticks=True),
                                              ui.input_slider("glycoscatter_height","Plot height",min=100,max=7500,step=100,value=500,ticks=True)
                                            )
                                          ),
                                      ui.output_ui("glycoscatter_ui"),
                                      ui.output_plot("glycoscatter")
                                      ),
                                ),icon=icon_svg("cubes-stacked")
                     ),
        ui.nav_panel("MOMA",
                     ui.navset_pill(
                         ui.nav_panel("MOMA Extraction",
                                      ui.card(
                                          ui.row(
                                              ui.input_slider("moma_mztolerance","m/z tolerance (m/z):",min=0,max=0.1,value=0.005,step=0.001,ticks=True),
                                              ui.input_slider("moma_rttolerance","Retention time tolerance (s):",min=0.1,max=2,value=0.5,step=0.1,ticks=True),
                                            ),
                                            ),
                                      ui.row(
                                          #parameters related to search file
                                          ui.column(6,
                                                    ui.card(
                                                        ui.card_header("From Search Result File(s)"),
                                                        ui.output_ui("moma_cond_rep_list"),
                                                        ui.input_slider("moma_imtolerance","Ion mobility tolerance (1/K0):",min=0.01,max=0.1,value=0.05,step=0.005,ticks=True),
                                                        ui.p("Table of Possible MOMA Events:"),
                                                        ui.output_data_frame("moma_events"),
                                                        )
                                                    ),
                                          #parameters related to raw file
                                          ui.column(6,
                                                    ui.card(
                                                        ui.card_header("From Raw File(s)"),
                                                        ui.input_radio_buttons("moma_file_or_folder","Load raw data from:",choices={"individual":"Individual Files","directory":"Directory"}),
                                                        ui.output_ui("moma_rawfile_input_ui"),
                                                        ui.output_ui("moma_rawfile_buttons_ui"),
                                                        ui.row(
                                                            ui.column(6,
                                                                    ui.input_action_button("moma_load_rawfile","Load Raw File",class_="btn-primary",width="300px"),
                                                                    ),
                                                            ui.column(6,
                                                                    ui.output_text_verbatim("file_uploaded"),
                                                                    )
                                                                ),
                                                        ui.row(
                                                            ui.column(6,
                                                                    ui.input_text("moma_mz","EIM m/z:"),
                                                                    ),
                                                            ui.column(6,
                                                                    ui.input_text("moma_rt","EIM Retention Time:"),
                                                                    )
                                                                ),
                                                        ui.output_plot("moma_eim")
                                                        )
                                                    )
                                            ),
                                      ui.download_button("momatable_download","Download MOMA Table",width="300px",icon=icon_svg("file-arrow-down")),
                                      ui.download_button("precursortable_download","Download Precursor Table",width="300px",icon=icon_svg("file-arrow-down"))
                                    )
                     ),icon=icon_svg("user-astronaut")
                    ),
        ui.nav_panel("De Novo",
                     ui.navset_pill(
                         ui.nav_panel("Secondary File Import",
                                      ui.card(
                                          ui.card_header("Important Reminders"),
                                          ui.p("-Use main File Import tab for the BPS Novor data, upload data for the software to compare it to in this tab"),
                                          ui.p("-Make sure that the condition names and replicate numbers are the same between the two metadata sheets")
                                             ),
                                      ui.card(
                                          ui.card_header("Upload Search Report"),
                                          ui.row(
                                              ui.column(3,
                                                        ui.input_radio_buttons("software_secondary","Search software:",{"spectronaut":"Spectronaut",
                                                                                                                        "diann":"DIA-NN (pre 2.0)",
                                                                                                                        "diann2.0":"DIA-NN (2.0)",
                                                                                                                        "fragpipe":"FragPipe",
                                                                                                                        "bps_timsrescore":"tims-rescore (BPS)",
                                                                                                                        "bps_timsdiann":"tims-DIANN (BPS)",
                                                                                                                        "bps_denovo":"BPS Novor"}),
                                                        ),
                                              ui.column(6,
                                                        ui.input_file("searchreport_secondary","Upload search report:",accept=[".tsv",".zip",".parquet"],multiple=True),
                                                        ui.output_text("metadata_reminder_secondary")
                                                       )
                                                ),
                                             ),
                                      ui.card(
                                          ui.card_header("Update from Metadata Table"),
                                          ui.row(
                                              ui.column(4,
                                                        ui.input_action_button("rerun_metadata_secondary","Apply Changes",width="300px",class_="btn-primary",icon=icon_svg("rotate"))
                                                       ),
                                              ui.column(4,
                                                        ui.input_switch("condition_names_secondary","Update 'R.Condition' and 'R.Replicate' columns",width="100%"),
                                                        ui.input_switch("remove_secondary","Remove selected runs")            
                                                       ),
                                              ui.column(4,
                                                        ui.input_switch("reorder_secondary","Reorder runs"),
                                                        ui.input_switch("concentration_secondary","Update 'Concentration' column")
                                                       )
                                                ),
                                            ),
                                      ui.card(
                                          ui.card_header("Metadata Tables"),
                                          ui.row(
                                              ui.column(4,
                                                        ui.input_file("metadata_upload_secondary","(Optional) Upload filled metadata table:",accept=".csv",multiple=False),
                                                        ui.input_switch("use_uploaded_metadata_secondary","Use uploaded metadata table"),
                                                       ),
                                              ui.column(4,
                                                        ui.download_button("metadata_download_secondary","Download metadata table as shown",width="300px",icon=icon_svg("file-arrow-down"))
                                                       ),
                                              ui.column(4,
                                                        ui.p("-To remove runs, add an 'x' to the 'remove' column"),
                                                        ui.p("-To reorder conditions, order them numerically in the 'order' column")
                                                       ),
                                                )
                                              ),
                                          ui.row(
                                              ui.column(8,
                                                        ui.output_data_frame("metadata_table_secondary")
                                                       ),
                                              ui.column(4,
                                                        ui.output_data_frame("metadata_condition_table_secondary")
                                                       )
                                                )
                                      ),
                         ui.nav_panel("Compare - Peptide Lengths",
                                      ui.card(
                                          ui.row(
                                              ui.input_slider("peplength_compare_width","Plot width",min=100,max=7500,step=100,value=1000,ticks=True),
                                              ui.input_slider("peplength_compare_height","Plot height",min=100,max=7500,step=100,value=600,ticks=True)
                                            )
                                          ),
                                      ui.output_ui("compare_len_samplelist"),
                                      ui.output_plot("peplength_compare_plot")
                                      ),
                         ui.nav_panel("Compare - Stripped Peptide IDs",
                                      ui.card(
                                          ui.row(
                                              ui.input_slider("denovocompare_venn_width","Plot width",min=100,max=7500,step=100,value=1000,ticks=True),
                                              ui.input_slider("denovocompare_venn_height","Plot height",min=100,max=7500,step=100,value=500,ticks=True)
                                            )
                                          ),
                                      ui.output_ui("denovocompare_venn_samplelist"),
                                      ui.input_switch("denovocompare_specific_length","Compare specific peptide length?",value=False,width="300px"),
                                      ui.output_ui("denovocompare_specific_length_ui"),
                                      ui.input_switch("denovocompare_peptidecore","Only consider peptide core (cut first and last 2 residues)",value=False,width="300px"),
                                      ui.download_button("denovocompare_venn_download","Download Peptide List",width="300px",icon=icon_svg("file-arrow-down")),
                                      ui.output_plot("denovocompare_venn_plot")
                                      ),
                         ui.nav_panel("Compare - Sequence Motifs",
                                      ui.row(
                                          ui.column(3,
                                                    ui.input_radio_buttons("seqmotif_compare_plottype","Pick kind of matrix to plot:",choices={"information":"Information","counts":"Counts"}),
                                                    ui.input_switch("seqmotif_compare_onlyunique","Use only unique BPS Novor IDs",value=False),
                                                    ui.input_slider("seqmotif_compare_peplengths","Pick peptide length to plot:",min=7,max=25,value=9,step=1,ticks=True),
                                                    ui.output_ui("seqmotif_compare_run_ui"),
                                                    ),
                                          ui.column(8,
                                                    ui.output_plot("seqmotif_compare_plot1"),
                                                    ui.output_plot("seqmotif_compare_plot2")
                                                    )
                                      )
                                      ),
                         ui.nav_panel("Compare - Sequence Motifs (Stats)",
                                      ui.row(
                                          ui.column(6,
                                                    ui.input_switch("seqmotif_compare_onlyunique2","Use only unique BPS Novor IDs",value=False),
                                                    ui.input_slider("seqmotif_compare_peplengths2","Pick peptide length to plot:",min=7,max=25,value=9,step=1,ticks=True),
                                                    ui.output_ui("seqmotif_compare_run_ui2"),
                                                    ui.output_plot("seqmotif_pca")
                                                    ),
                                          ui.column(6,
                                                    ui.input_slider("seqmotif_3d_azimuth","3D Plot - Azimuth Angle",min=0,max=360,value=0,step=5,ticks=True),
                                                    ui.input_slider("seqmotif_3d_elevation","3D Plot - Elevation Angle",min=0,max=90,value=0,step=5,ticks=True),
                                                    ui.output_plot("seqmotif_3d")
                                                    )
                                      )
                                      ),
                         ui.nav_panel("IDs Found in Fasta",
                                      ui.card(
                                          ui.row(
                                              ui.input_slider("fasta_width","Plot width",min=100,max=7500,step=100,value=1000,ticks=True),
                                              ui.input_slider("fasta_height","Plot height",min=100,max=7500,step=100,value=600,ticks=True)
                                            )
                                          ),
                                      ui.output_plot("fasta_plot")
                                      ),
                         ui.nav_panel("Position Confidence",
                                      ui.card(
                                          ui.row(
                                              ui.input_slider("confidence_width","Plot width",min=100,max=7500,step=100,value=800,ticks=True),
                                              ui.input_slider("confidence_height","Plot height",min=100,max=7500,step=100,value=1000,ticks=True)
                                            )
                                          ),
                                      ui.row(
                                          ui.column(4,
                                                    ui.output_ui("confidence_condition_ui"),
                                                    ui.input_slider("confidence_lengthslider","Pick peptide length to plot for:",min=7,max=20,step=1,value=9,ticks=True)
                                                    ),
                                          ui.column(8,
                                                    ui.output_plot("confidence_plot")
                                                    )   
                                            ),
                                      ),
                                ),icon=icon_svg("atom")
                     ),
        ui.nav_panel("Two-Software Comparison",
                     ui.navset_pill(
                         ui.nav_panel("File Import",
                                      ui.card(
                                          ui.card_header("Upload Search Reports"),
                                          ui.row(
                                              ui.column(4,
                                                  ui.input_file("compare_searchreport1","Upload first search report:",accept=[".tsv",".zip",".parquet"],multiple=True),
                                                  ui.input_radio_buttons("compare_software1","First search software:",{"spectronaut":"Spectronaut",
                                                                                            "diann":"DIA-NN (pre 2.0)",
                                                                                            "diann2.0":"DIA-NN (2.0)",
                                                                                            "fragpipe":"FragPipe",
                                                                                            "bps_timsrescore":"tims-rescore (BPS)",
                                                                                            "bps_timsdiann":"tims-DIANN (BPS)",
                                                                                            "bps_denovo":"BPS Novor"
                                                                                            })
                                                  ),
                                              ui.column(4,
                                                  ui.input_file("compare_searchreport2","Upload second search report:",accept=[".tsv",".zip",".parquet"],multiple=True),
                                                  ui.input_radio_buttons("compare_software2","Second search software:",{"spectronaut":"Spectronaut",
                                                                                            "diann":"DIA-NN (pre 2.0)",
                                                                                            "diann2.0":"DIA-NN (2.0)",
                                                                                            "fragpipe":"FragPipe",
                                                                                            "bps_timsrescore":"tims-rescore (BPS)",
                                                                                            "bps_timsdiann":"tims-DIANN (BPS)",
                                                                                            "bps_denovo":"BPS Novor"
                                                                                            })
                                                  )
                                                ),
                                            ),
                                      ui.card(
                                          ui.card_header("Update from Metadata Table"),
                                          ui.row(
                                              ui.column(3,
                                                        ui.input_action_button("compare_rerun_metadata","Apply Changes",width="300px",class_="btn-primary",icon=icon_svg("rotate"))
                                                        ),
                                              ui.input_switch("compare_remove","Remove selected runs"),
                                              ui.input_switch("compare_reorder","Reorder runs"),
                                              ui.input_switch("compare_concentration","Update 'Concentration' column")
                                              )
                                          ),
                                      ui.card(
                                          ui.card_header("Metadata Tables"),
                                          ui.row(
                                              ui.column(4,
                                                      ui.input_file("compare_metadata_upload","(Optional) Upload filled metadata table:",accept=".csv",multiple=False),
                                                      ui.input_switch("compare_use_uploaded_metadata","Use uploaded metadata table"),
                                                      ),
                                              ui.column(4,
                                                      ui.download_button("compare_metadata_download","Download metadata table as shown",width="300px",icon=icon_svg("file-arrow-down"))
                                                      ),
                                                ),
                                          ui.row(
                                              ui.column(9,
                                                        ui.output_data_frame("compare_metadata_table"),
                                                        ),
                                              ui.column(3,
                                                        ui.output_data_frame("compare_metadata_condition_table")
                                                        )
                                                ),
                                            ),
                                      ),
                          ui.nav_panel("ID Counts",
                                       ui.card(
                                           ui.row(
                                               ui.input_slider("compare_id_counts_width","Plot width",min=100,max=7500,step=100,value=1500,ticks=True),
                                               ui.input_slider("compare_id_counts_height","Plot height",min=100,max=7500,step=100,value=1000,ticks=True)
                                               )
                                            ),
                                       ui.output_plot("compare_id_counts")
                                       ),
                          ui.nav_panel("Venn Diagram",
                                       ui.card(
                                           ui.row(
                                               ui.input_slider("compare_venn_width","Plot width",min=100,max=7500,step=100,value=1000,ticks=True),
                                               ui.input_slider("compare_venn_height","Plot height",min=100,max=7500,step=100,value=500,ticks=True)
                                            )
                                        ),
                                       ui.row(
                                           ui.column(4,
                                                     ui.input_radio_buttons("compare_venn_conditionorrun","Plot by condition or individual run?",choices={"condition":"Condition","individual":"Individual Run"}),
                                                     ui.input_radio_buttons("compare_venn_plotproperty","Metric to compare:",choices={"proteingroups":"Protein Groups","peptides":"Peptides","precursors":"Precursors","peptides_stripped":"Stripped Peptides",}),
                                                     #ui.input_switch("compare_venn_specific_length","Compare specific peptide length?",value=False,width="300px"),
                                                     ui.output_ui("compare_venn_ptm_ui"),
                                                     ui.output_ui("compare_venn_ptmlist_ui"),
                                                     ui.output_ui("compare_venn_specific_length_ui"),
                                                     ui.output_ui("compare_venn_peplength_ui")
                                                   ),
                                           ui.column(4,
                                                     ui.output_ui("compare_venn_run_ui"),
                                                     ui.download_button("compare_venn_download","Download Venn list",width="300px",icon=icon_svg("file-arrow-down"))
                                                   )
                                       ),
                                       ui.output_plot("compare_venn_plot")
                                     ),
                        ),icon=icon_svg("code-compare")
                    ),
        ui.nav_panel("Export Tables",
                     ui.navset_pill(
                         ui.nav_panel("Export Tables",
                                      ui.card(
                                          ui.card_header("Table of Peptide IDs"),
                                          ui.download_button("peptidelist","Download Peptide IDs",width="300px",icon=icon_svg("file-arrow-down")),
                                          ),
                                      ui.card(
                                          ui.card_header("Table of Stripped Peptide IDs (Specific Length)"),
                                          ui.row(
                                              ui.column(4,
                                                        ui.download_button("strippedpeptidelist","Download Stripped Peptide IDs",width="300px",icon=icon_svg("file-arrow-down"))),
                                              ui.column(4,
                                                        ui.input_radio_buttons("peptidelist_condition_or_run","Condition or individual run?",choices={"condition":"condition","individual":"individual run"}),
                                                        ui.input_slider("strippedpeptidelength","Pick specific peptide length to export:",min=7,max=25,value=9,step=1,ticks=True)),
                                              ui.column(4,
                                                        ui.output_ui("peptidelist_dropdown")
                                                        )
                                          )
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
                                                        ui.input_slider("rttolerance","Retention time tolerance (s):",min=0.1,max=2,value=0.5,step=0.1,ticks=True),
                                                        ui.input_slider("mztolerance","m/z tolerance (m/z):",min=0.0005,max=0.1,value=0.005,step=0.0005,ticks=True)
                                                        ),
                                              ui.column(4,
                                                        ui.input_slider("imtolerance","Ion mobility tolerance (1/K0)",min=0.01,max=0.1,value=0.05,step=0.005,ticks=True)
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
        ui.nav_panel("Raw Data",
                     ui.navset_pill(
                         ui.nav_panel("Multi-File Import",
                                      ui.p("Note: this section is independent of what has been uploaded to the File Import tab"),
                                      ui.input_radio_buttons("file_or_folder","Load raw data from:",choices={"individual":"Individual Files","directory":"Directory"}),
                                      ui.output_ui("rawfile_input_ui"),
                                      ui.output_text_verbatim("uploadedfiles")
                                      ),
                         ui.nav_panel("TIC Plot",
                                      ui.card(
                                          ui.row(
                                              ui.input_slider("tic_width","Plot width",min=100,max=7500,step=100,value=1500,ticks=True),
                                              ui.input_slider("tic_height","Plot height",min=100,max=7500,step=100,value=600,ticks=True)
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
                                              ui.input_slider("bpc_width","Plot width",min=100,max=7500,step=100,value=1500,ticks=True),
                                              ui.input_slider("bpc_height","Plot height",min=100,max=7500,step=100,value=600,ticks=True)
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
                                              ui.input_slider("accutime_width","Plot width",min=100,max=7500,step=100,value=1500,ticks=True),
                                              ui.input_slider("accutime_height","Plot height",min=100,max=7500,step=100,value=600,ticks=True)
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
                                          ui.row(
                                              ui.column(4,
                                                        ui.output_ui("rawfile_buttons_eic"),
                                                        ui.input_action_button("eic_load_rawfile","Load Raw File",width="300px",class_="btn-primary")
                                                        ),
                                              ui.column(4,
                                                        ui.input_text("eic_mz_input","Input m/z for EIC:"),
                                                        ui.input_text("eic_ppm_input","Input mass error (ppm) for EIC:"),
                                                        ),
                                              ui.column(4,
                                                        ui.input_switch("include_mobility","Include mobility in EIC"),
                                                        ui.output_ui("mobility_input")
                                                        ),
                                                ),
                                          ),
                                      ui.card(
                                          ui.row(
                                              ui.input_slider("eic_width","Plot width",min=100,max=7500,step=100,value=1500,ticks=True),
                                              ui.input_slider("eic_height","Plot height",min=100,max=7500,step=100,value=600,ticks=True)
                                            )
                                          ),
                                      ui.output_plot("eic")
                                      ),
                         ui.nav_panel("EIM Plot",
                                      ui.card(
                                          ui.row(
                                              ui.column(4,
                                                        ui.output_ui("rawfile_buttons_eim"),
                                                        ui.input_action_button("eim_load_rawfile","Load Raw File",width="300px",class_="btn-primary")
                                                        ),
                                              ui.column(4,
                                                        ui.input_text("eim_mz_input","Input m/z for EIM:"),
                                                        ui.input_text("eim_ppm_input","Input mass error (ppm) for EIM:"),
                                                        ),
                                                ),
                                          ),
                                      ui.card(
                                          ui.row(
                                              ui.input_slider("eim_width","Plot width",min=100,max=7500,step=100,value=1500,ticks=True),
                                              ui.input_slider("eim_height","Plot height",min=100,max=7500,step=100,value=600,ticks=True)
                                            )
                                          ),
                                      ui.output_plot("eim")
                                      ),
                         ),icon=icon_svg("desktop")
                     ),
    widths=(2,8)
    ),
    theme=theme.cerulean()
)
#endregion

# ============================================================================= Library Imports (all others needed for calculations)
#region
import alphatims.bruker as atb
import alphatims.plotting as atp
from collections import OrderedDict
from datetime import date
import io
import itertools
from itertools import groupby
import logomaker as lm
import math
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors
from matplotlib.patches import Rectangle
from matplotlib.ticker import MaxNLocator,MultipleLocator
from matplotlib_venn import venn2,venn2_circles,venn3,venn3_circles
import numpy as np
import os
import pandas as pd
import pathlib
import re
import scipy.stats as stats
from scipy.stats import norm
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from tkinter import *
from upsetplot import *
from zipfile import ZipFile

matplotlib.use('Agg')
#endregion

# =============================================================================
# Server
# =============================================================================

def server(input: Inputs, output: Outputs, session: Session):

# ============================================================================= Metrics Functions for Plotting
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
            maxreplicates=len(samplegroup["R.Replicate"].drop_duplicates().tolist())
            maxreplicatelist.append(maxreplicates)
        averagedf=pd.DataFrame({"R.Condition":sampleconditions,"N.Replicates":maxreplicatelist})
        numconditions=len(averagedf["R.Condition"].tolist())
        repspercondition=averagedf["N.Replicates"].tolist()
        numsamples=len(resultdf["R.Condition"].tolist())
        if input.dpi_switch()==True:
            matplotlib.rcParams["figure.dpi"]=300
        else:
            matplotlib.rcParams["figure.dpi"]=100

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
            numproteins.append(replicatedata["PG.ProteinGroups"].nunique())
            #identified proteins with 2 peptides
            numproteins2pepts.append(len(replicatedata[["PG.ProteinGroups","EG.ModifiedPeptide"]].drop_duplicates().groupby("PG.ProteinGroups").size().reset_index(name="peptides").query("peptides>1")))
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
                cvproteintable=cvproteintable.loc[(cvproteintable!=0).any(axis=1)]
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
                cvprecursortable=cvprecursortable.loc[(cvprecursortable!=0).any(axis=1)]
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

        #peptide-level CVs
        if input.peptide_grouping()=="stripped":
            grouping_key="PEP.StrippedSequence"
        if input.peptide_grouping()=="modified":
            grouping_key="EG.ModifiedPeptide"

        peptidecvlist=[]
        peptidecvlist95=[]
        peptidecvdict={}
        for x,condition in enumerate(searchoutput["R.Condition"].drop_duplicates().tolist()):
            df=searchoutput[searchoutput["R.Condition"]==condition]
            placeholderdf=pd.DataFrame()
            if maxreplicatelist[x]==1:
                emptylist=[]
                peptidecvlist.append(emptylist)
                peptidecvlist95.append(emptylist)
            else:
                for run in searchoutput["Cond_Rep"].drop_duplicates().tolist():
                    df1=df[df["Cond_Rep"]==run][[grouping_key,"FG.MS2Quantity"]].groupby(grouping_key).head(3).groupby(grouping_key).mean()
                    placeholderdf=pd.concat([placeholderdf,df1],axis=0)
                mean=placeholderdf.sort_values(grouping_key).groupby(grouping_key).mean()
                std=placeholderdf.sort_values(grouping_key).groupby(grouping_key).std()
                cv=(std/mean)*100
                cv=cv["FG.MS2Quantity"].dropna().tolist()
                peptidecvlist.append(cv)
                peptidecvdict[condition]=pd.DataFrame(cv,columns=["CV"])

                top95=np.percentile(cv,95)
                cvlist95=[]
                for i in cv:
                    if i <=top95:
                        cvlist95.append(i)
                peptidecvlist95.append(cvlist95)
    
        cvcalc_df["Peptide CVs"]=peptidecvlist
        cvcalc_df["Peptide 95% CVs"]=peptidecvlist95

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

        #peptide CVs
        peptidescv20=[]
        peptidescv10=[]
        for x,condition in enumerate(sampleconditions):
            if maxreplicatelist[x]==1:
                emptylist=[]
                peptidescv20.append(emptylist)
                peptidescv10.append(emptylist)
            else:
                peptidescv20.append(peptidecvdict[condition][peptidecvdict[condition]["CV"]<20].shape[0])
                peptidescv10.append(peptidecvdict[condition][peptidecvdict[condition]["CV"]<10].shape[0])

        cvcalc_df["peptidesCV<20"]=peptidescv20
        cvcalc_df["peptidesCV<10"]=peptidescv10

        return cvcalc_df

    #charge states
    @reactive.calc
    def chargestates():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()

        chargestatedf_condition=pd.DataFrame()
        chargestatedf_run=pd.DataFrame()

        chargestatelist=[]
        chargestategroup=searchoutput[["R.Condition","EG.ModifiedPeptide","FG.Charge"]].drop_duplicates().reset_index(drop=True)
        for condition in sampleconditions:
            df=pd.DataFrame(chargestategroup[chargestategroup["R.Condition"]==condition].drop(columns=["R.Condition","EG.ModifiedPeptide"]))
            chargestatelist.append(df["FG.Charge"].tolist())
        chargestatedf_condition["Sample Names"]=sampleconditions
        chargestatedf_condition["Charge States"]=chargestatelist

        chargestatelist=[]
        chargestategroup=searchoutput[["Cond_Rep","EG.ModifiedPeptide","FG.Charge"]].drop_duplicates().reset_index(drop=True)
        for run in searchoutput["Cond_Rep"].drop_duplicates().reset_index(drop=True):
            df=pd.DataFrame(chargestategroup[chargestategroup["Cond_Rep"]==run].drop(columns=["Cond_Rep","EG.ModifiedPeptide"]))
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
            df=searchoutput[searchoutput["R.Condition"]==condition][["PG.ProteinGroups","EG.ModifiedPeptide"]].drop_duplicates().reset_index(drop=True)
            pepsperproteinlist.append(df.groupby(["PG.ProteinGroups"]).size().tolist())
        pepsperprotein_condition["Sample Names"]=sampleconditions
        pepsperprotein_condition["Peptides per Protein"]=pepsperproteinlist

        pepsperproteinlist=[]
        for run in searchoutput["Cond_Rep"].drop_duplicates().reset_index(drop=True):
            df=searchoutput[searchoutput["Cond_Rep"]==run][["PG.ProteinGroups","EG.ModifiedPeptide"]].drop_duplicates().reset_index(drop=True)
            pepsperproteinlist.append(df.groupby(["PG.ProteinGroups"]).size().tolist())
        pepsperprotein_run["Sample Names"]=searchoutput["Cond_Rep"].drop_duplicates().reset_index(drop=True)
        pepsperprotein_run["Peptides per Protein"]=pepsperproteinlist

        return pepsperprotein_condition,pepsperprotein_run

    #peak widths
    @reactive.calc
    def peakwidths():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()

        fwhm_df=pd.DataFrame()
        fwhm_df["Cond_Rep"]=searchoutput["Cond_Rep"].drop_duplicates().reset_index(drop=True)
        peakwidths=[]
        peakwidths_95=[]
        for run in searchoutput["Cond_Rep"].drop_duplicates().tolist():
            peakwidthlist=(searchoutput[searchoutput["Cond_Rep"]==run]["EG.PeakWidth"]*60).tolist()
            peakwidths.append(peakwidthlist)
            top95=np.percentile(peakwidthlist,95)
            top95list=[]
            for i in peakwidthlist:
                if i <= top95:
                    top95list.append(i)
            peakwidths_95.append(top95list)
        fwhm_df["Peak Width"]=peakwidths
        fwhm_df["Peak Width 95%"]=peakwidths_95

        return fwhm_df

#endregion

# =============================# Sidebar Tabs #================================
# ============================================================================= File Import
#region

    #import search report file
    @reactive.calc
    def inputfile():
        if input.searchreport() is None:
            return pd.DataFrame()
        if ".tsv" in input.searchreport()[0]["name"]:
            if len(input.searchreport())>1:
                searchoutput=pd.DataFrame()
                for i in range(len(input.searchreport())):
                    run=pd.read_csv(input.searchreport()[i]["datapath"],sep="\t")
                    searchoutput=pd.concat([searchoutput,run])
            else:
                searchoutput=pd.read_csv(input.searchreport()[0]["datapath"],sep="\t")
            if input.software()=="diann":
                searchoutput.rename(columns={"Run":"R.FileName"},inplace=True)
                searchoutput.insert(1,"R.Condition","")
                searchoutput.insert(2,"R.Replicate","")
                searchoutput["EG.PeakWidth"]=searchoutput["RT.Stop"]-searchoutput["RT.Start"]

                if input.diann_mbr_switch()==False:
                    searchoutput=searchoutput[searchoutput["Protein.Q.Value"]<=0.01]
                if input.diann_mbr_switch()==True:
                    searchoutput=searchoutput[searchoutput["Global.PG.Q.Value"]<=0.01]

                searchoutput.drop(columns=["File.Name","PG.Normalized","PG.MaxLFQ","Genes.Quantity",
                                            "Genes.Normalised","Genes.MaxLFQ","Genes.MaxLFQ.Unique","Precursor.Id",
                                            "PEP","Global.Q.Value","GG.Q.Value",#"Protein.Q.Value","Global.PG.Q.Value",
                                            "Translated.Q.Value","Precursor.Translated","Translated.Quality","Ms1.Translated",
                                            "Quantity.Quality","RT.Stop","RT.Start","iRT","Predicted.iRT",
                                            "First.Protein.Description","Lib.Q.Value","Lib.PG.Q.Value","Ms1.Profile.Corr",
                                            "Ms1.Area","Evidence","Spectrum.Similarity","Averagine","Mass.Evidence",
                                            "Decoy.Evidence","Decoy.CScore","Fragment.Quant.Raw","Fragment.Quant.Corrected",
                                            "Fragment.Correlations","MS2.Scan","iIM","Predicted.IM",
                                            "Predicted.iIM","PG.Normalised","PTM.Informative","PTM.Specific","PTM.Localising",
                                            "PTM.Q.Value","PTM.Site.Confidence","Lib.PTM.Site.Confidence"],inplace=True,errors='ignore')

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
                        "UniMod:7":"Deamidation (NQ)",
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
            if input.software()=="fragpipe":
                searchoutput.rename(columns={"Spectrum File":"R.FileName"},inplace=True)
                searchoutput.insert(1,"R.Condition","")
                searchoutput.insert(2,"R.Replicate","")
                
                searchoutput["FG.CalibratedMassAccuracy (PPM)"]=(searchoutput["Delta Mass"]/searchoutput["Calculated M/Z"])*10E6

                searchoutput.drop(columns=["Spectrum","Extended Peptide","Prev AA","Next AA","Peptide Length",
                                        "Observed Mass","Calibrated Observed Mass","Calibrated Observed M/Z",
                                        "Calculated Peptide Mass","Calculated M/Z","Delta Mass",
                                        "Expectation","Hyperscore","Nextscore",
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
                    "43":"Acetyl (Protein N-term)",
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
                #if the Spectrum File column is just a single value, get the file names from the Spectrum column
                if searchoutput["Spectrum"][0].split(".")[0] not in searchoutput["Spectrum File"][0]:
                    fragger_filelist=searchoutput["Spectrum"].str.split(".",expand=True).drop(columns=[1,2,3]).drop_duplicates().reset_index(drop=True)
                    fragger_filelist.rename(columns={0:"R.FileName"},inplace=True)

                    filenamelist=[]
                    for run in fragger_filelist["R.FileName"]:
                        fileindex=fragger_filelist[fragger_filelist["R.FileName"]==run].index.values[0]
                        filenamelist.append([fragger_filelist["R.FileName"][fileindex]]*len(searchoutput[searchoutput["Spectrum"].str.contains(run)]))

                    searchoutput.insert(0,"R.FileName",list(itertools.chain(*filenamelist)))
                    searchoutput.drop(columns=["Spectrum File"],inplace=True)

                else:
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

                #remove the "% glycan m/z" from the Total Glycan Composition
                searchoutput["Total Glycan Composition"]=searchoutput["Total Glycan Composition"].str.split("%",expand=True)[0]
        
        #for BPS input
        if ".zip" in input.searchreport()[0]["name"]:
            os.chdir(os.path.dirname(os.path.realpath(__file__)))
            searchoutput=pd.DataFrame()
            bpszip=ZipFile(input.searchreport()[0]["datapath"])
            bpszip.extractall()
            metadata_bps=pd.read_csv("metadata.csv")
            runlist=metadata_bps["processing_run_uuid"].tolist()
            cwd=os.getcwd()+"\\processing-run"
            os.chdir(cwd)

            if input.software()=="bps_timsrescore":
                peptide_dict=dict()
                samplename_list=[]
                for run in runlist:
                    os.chdir(cwd)
                    os.chdir(cwd+"\\"+run)
                    pgfdr_peptide=pd.read_parquet("pgfdr.peptide.parquet")
                    peptide_dict[run]=pgfdr_peptide

                #filter, rename/remove columns, and generate ProteinGroups and ProteinNames columns from protein_list column
                for key in peptide_dict.keys():
                    df=peptide_dict[key][(peptide_dict[key]["protein_list"].str.contains("Reverse")==False)&(peptide_dict[key]["protein_list"].str.contains("contaminant")==False)].reset_index(drop=True)
                    df=df.rename(columns={"sample_name":"R.FileName",
                                    "stripped_peptide":"PEP.StrippedSequence",
                                    "precursor_mz":"FG.PrecMz",
                                    "rt":"EG.ApexRT",
                                    "charge":"FG.Charge",
                                    "ook0":"EG.IonMobility",
                                    "ppm_error":"FG.CalibratedMassAccuracy (PPM)"})

                    proteingroups=[]
                    proteinnames=[]
                    proteinlist_column=df["protein_list"].tolist()
                    for item in proteinlist_column:
                        if item.count(";")==0:
                            templist=item.split("|")
                            proteingroups.append(templist[1])
                            proteinnames.append(templist[2])
                        else:
                            proteingroups_torejoin=[]
                            proteinnames_torejoin=[]
                            for entry in item.split(";"):
                                templist=entry.split("|")
                                proteingroups_torejoin.append(templist[1])
                                proteinnames_torejoin.append(templist[2])
                            proteingroups.append(";".join(proteingroups_torejoin))
                            proteinnames.append(";".join(proteinnames_torejoin))
                    df["PG.ProteinGroups"]=proteingroups
                    df["PG.ProteinNames"]=proteinnames
                    
                    #adding a q-value filter before dropping the column
                    df=df[df["global_peptide_qvalue"]<=0.01]

                    df=df.drop(columns=["index","processing_run_uuid","ms2_id","candidate_id","protein_group_parent_id",
                                    "protein_group_name","leading_aa","trailing_aa","mokapot_psm_score","mokapot_psm_qvalue",
                                    "mokapot_psm_pep","mokapot_peptide_qvalue","mokapot_peptide_pep","global_peptide_score",
                                    "x_corr_score","delta_cn_score","precursor_mh","calc_mh","protein_list","is_contaminant",
                                    "is_target","number_matched_ions","global_peptide_qvalue"],errors='ignore')
                    
                    searchoutput=pd.concat([searchoutput,df],ignore_index=True)

                #rename ptms 
                searchoutput=searchoutput.reset_index(drop=True)
                searchoutput["ptms"]=searchoutput["ptms"].astype(str)
                searchoutput["ptms"]=searchoutput["ptms"].replace({
                        "42.010565":"Acetyl (Protein N-term)",
                        "57.021464":"Carbamidomethyl (C)",
                        "79.966331":"Phospho (STY)",
                        "15.994915":"Oxidation (M)"},regex=True)

                searchoutput["ptm_locations"]=searchoutput["ptm_locations"].astype(str)
                searchoutput["ptm_locations"]=searchoutput["ptm_locations"].str.replace("[]","-1").str.replace("[","").str.replace("]","")

                #build and add the EG.ModifiedPeptide column
                modifiedpeptides=[]
                for i,entry in enumerate(searchoutput["ptm_locations"]):
                    if entry=="-1":
                        modifiedpeptides.append(searchoutput["PEP.StrippedSequence"][i])
                    else:
                        str_to_list=list(searchoutput["PEP.StrippedSequence"][i])
                        if len(searchoutput["ptm_locations"][i])==1:
                            mod_loc=int(searchoutput["ptm_locations"][i])+1
                            mod_add=searchoutput["ptms"][i]
                            str_to_list.insert(mod_loc,mod_add)
                            modifiedpeptides.append("".join(str_to_list))
                        #if theres >1 ptm, we need to reformat some strings so we can insert them in the sequence
                        else:
                            ptmlocs=searchoutput["ptm_locations"][i].strip().split(" ")
                            ptms=searchoutput["ptms"][i].replace("[","").replace("]","").replace(") ","),").split(",")
                            for ele in ptmlocs:
                                if ele=="":
                                    ptmlocs.remove(ele)
                            ptms_for_loop=[]
                            for ele in ptms:
                                ptms_for_loop.append("["+ele+"]")
                            for j,loc in enumerate(ptmlocs):
                                mod_loc=int(loc)+j+1
                                mod_add=ptms_for_loop[j]
                                str_to_list.insert(mod_loc,mod_add)
                            modifiedpeptides.append("".join(str_to_list))
                searchoutput["EG.ModifiedPeptide"]=modifiedpeptides
                searchoutput=searchoutput.drop(columns=["ptms","ptm_locations"])

                searchoutput.insert(1,"R.Condition","")
                searchoutput.insert(2,"R.Replicate","")
                
                #change the cwd back to the code file since we changed it to the uploaded file 
                os.chdir(os.path.dirname(os.path.realpath(__file__)))
            if input.software()=="bps_timsdiann":
                for run in runlist:
                    os.chdir(cwd)
                    os.chdir(os.getcwd()+"\\"+run)
                    bps_resultzip=ZipFile("tims-diann.result.zip")
                    bps_resultzip.extractall()
                    results=pd.read_csv("results.tsv",sep="\t")
                    searchoutput=pd.concat([searchoutput,results])

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
                                        "Precursor.Calibrated.Mz","Fragment.Info","Fragment.Calibrated.Mz","Lib.1/K0",
                                        "Precursor.Normalised"],inplace=True,errors='ignore')

                searchoutput.rename(columns={"File.Name":"R.FileName",
                                            "Protein.Group":"PG.ProteinGroups",
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

                searchoutput.insert(1,"R.Condition","")
                searchoutput.insert(2,"R.Replicate","")
                
                #change the cwd back to the code file since we changed it to the uploaded file 
                os.chdir(os.path.dirname(os.path.realpath(__file__)))
            if input.software()=="bps_denovo":
                denovo_score=65.0
                peptide_dict=dict()
                protein_dict=dict()
                for run in runlist:
                    os.chdir(cwd)
                    #change working dir to next processing run subfolder
                    os.chdir(cwd+"\\"+run)

                    peptide_dict[run]=pd.read_parquet("novor-fasta-mapping-results.peptide.parquet")
                    protein_dict[run]=pd.read_parquet("novor-fasta-mapping-results.protein.parquet")

                for key in peptide_dict.keys():
                    peptideparquet=peptide_dict[key]
                    proteinparquet=protein_dict[key]

                    #filter parquet file
                    peptideparquet=peptideparquet[(peptideparquet["denovo_score"]>=denovo_score)&(peptideparquet["rank"]==1)].reset_index(drop=True)

                    #rename columns
                    peptideparquet.rename(columns={"sample_name":"R.FileName",
                                                "stripped_peptide":"PEP.StrippedSequence",
                                                "precursor_mz":"FG.PrecMz",
                                                "charge":"FG.Charge",
                                                "ppm_error":"FG.CalibratedMassAccuracy (PPM)",
                                                "rt":"EG.ApexRT",
                                                "ook0":"EG.IonMobility",
                                                "precursor_intensity":"FG.MS2Quantity"
                                                },inplace=True)

                    #drop columns
                    peptideparquet.drop(columns=["index","processing_run_id","ms2_id","rank","leading_aa","trailing_aa","precursor_mh",
                                                "calc_mh","denovo_tag_length","found_in_dbsearch","denovo_matches_db",
                                                "protein_group_parent_loc","protein_group_parent_list_loc","protein_group_parent_list_id"
                                                ],inplace=True,errors='ignore')
                    #fill NaN in the protein group column with -1
                    peptideparquet["protein_group_parent_id"]=peptideparquet["protein_group_parent_id"].fillna(-1)

                    #pull protein and gene info from protein parquet file and add to df 
                    protein_name=[]
                    protein_accession=[]
                    gene_id=[]
                    uncategorized_placeholder="uncat"

                    for i in range(len(peptideparquet["protein_group_parent_id"])):
                        if peptideparquet["protein_group_parent_id"][i]==-1:
                            protein_name.append(uncategorized_placeholder)
                            protein_accession.append(uncategorized_placeholder)
                            gene_id.append(uncategorized_placeholder)
                        else:
                            protein_name.append(proteinparquet["protein_name"].iloc[int(peptideparquet["protein_group_parent_id"][i])])
                            protein_accession.append(proteinparquet["protein_accession"].iloc[int(peptideparquet["protein_group_parent_id"][i])])
                            gene_id.append(proteinparquet["gene_id"].iloc[int(peptideparquet["protein_group_parent_id"][i])])

                    peptideparquet["PG.ProteinGroups"]=protein_name
                    peptideparquet["PG.ProteinAccessions"]=protein_accession
                    peptideparquet["PG.Genes"]=gene_id
                    peptideparquet=peptideparquet.drop(columns=["protein_group_parent_id"])

                    searchoutput=pd.concat([searchoutput,peptideparquet],ignore_index=True)

                #rename PTMs
                searchoutput["ptms"]=searchoutput["ptms"].astype(str)
                searchoutput["ptms"]=searchoutput["ptms"].replace({"57.0215":"Carbamidomethyl (C)",
                                                                   "15.994915":"Oxidation (M)",
                                                                   "15.9949":"Oxidation (M)",
                                                                   "79.966331":"Phospho (STY)",
                                                                   "0.984":"Deamidation (NQ)",
                                                                   },regex=True)
                searchoutput["ptm_locations"]=searchoutput["ptm_locations"].astype(str)
                searchoutput["ptm_locations"]=searchoutput["ptm_locations"].str.replace("[]","[-1]").str.replace("[","").str.replace("]","")

                #build and add the EG.ModifiedPeptide column
                modifiedpeptides=[]
                for i,entry in enumerate(searchoutput["ptm_locations"]):
                    if entry=="-1":
                        modifiedpeptides.append(searchoutput["PEP.StrippedSequence"][i])
                    else:
                        str_to_list=list(searchoutput["PEP.StrippedSequence"][i])
                        if len(searchoutput["ptm_locations"][i])==1:
                            mod_loc=int(searchoutput["ptm_locations"][i])+1
                            mod_add=searchoutput["ptms"][i]
                            str_to_list.insert(mod_loc,mod_add)
                            modifiedpeptides.append("".join(str_to_list))
                        #if theres >1 ptm, we need to reformat some strings so we can insert them in the sequence
                        else:
                            ptmlocs=searchoutput["ptm_locations"][i].strip().split(" ")
                            ptms=searchoutput["ptms"][i].replace("[","").replace("]","").replace(") ","),").split(",")
                            for ele in ptmlocs:
                                if ele=="":
                                    ptmlocs.remove(ele)
                            ptms_for_loop=[]
                            for ele in ptms:
                                ptms_for_loop.append("["+ele+"]")
                            for j,loc in enumerate(ptmlocs):
                                mod_loc=int(loc)+j+1
                                mod_add=ptms_for_loop[j]
                                str_to_list.insert(mod_loc,mod_add)
                            modifiedpeptides.append("".join(str_to_list))
                searchoutput["EG.ModifiedPeptide"]=modifiedpeptides
                searchoutput=searchoutput.drop(columns=["ptms","ptm_locations"])

                searchoutput.insert(1,"R.Condition","")
                searchoutput.insert(2,"R.Replicate","")

                #change the cwd back to the code file since we changed it to the uploaded file 
                os.chdir(os.path.dirname(os.path.realpath(__file__)))
            if input.software()=="glycoscape":
                results_dict=dict()
                for run in runlist:
                    os.chdir(cwd)
                    #change working dir to next processing run subfolder
                    os.chdir(cwd+"\\"+run)

                    results_dict[run]=pd.read_parquet("myriad-merger.glycopsm.parquet")

                for key in results_dict.keys():
                    parquet=results_dict[key]

                    #filter parquet file
                    parquet=parquet[parquet["mokapot_psm_qvalue"]<=0.01].reset_index(drop=True)

                    parquet.rename(columns={"sample_name":"R.FileName",
                                                "stripped_peptide":"PEP.StrippedSequence",
                                                "observed_precursor_mz":"FG.PrecMz",
                                                "precursor_charge":"FG.Charge",
                                                "rt":"EG.ApexRT",
                                                "ook0":"EG.IonMobility",
                                                "peptide_ppm_error":"FG.CalibratedMassAccuracy (PPM)",
                                                },inplace=True)

                    parquet.drop(columns=["index","processing_run_uuid","ms2_id","peptide_candidate_id","glycan_candidate_id",
                                            "protein_group_parent_id","protein_group_name","leading_aa","trailing_aa","hexnac_modification",
                                            "glycosylation_motif","is_contaminant","is_target","peptide_mh","peptide_calc_mh",
                                            "peptide_isotope_offset","x_corr_score","delta_cn_score","number_matched_ions",
                                            "mokapot_psm_score","mokapot_psm_pep","mokapot_peptide_qvalue","mokapot_peptide_pep",
                                            "global_peptide_score","Y1_mz","Y1_charge","experimental_glycan_mr","glycan_isotope_offset",
                                            "glycan_composition_mass","filtered_glycan_rank","ambiguous_glycan_composition",
                                            "glycan_rank","building_blocks_coverage","fucose_evidence","Y5Y1_evidence","has_core",
                                            "sia_smaller_hn","composition_oxonium_count","composition_oxonium_intensity",
                                            "spectrum_oxonium_count","oxonium_relative_intensity_sum","fucose_shadow_count",
                                            "fucose_shadow_intensity_sum","bb_names","bb_oxonium_count","bb_oxonium_intensity",
                                            "oxonium_ions_names","oxonium_ions_mzs","oxonium_ions_intensity","Y_ions_names",
                                            "oxonium_relative_intensity_sum","Y_ions_mass_offset","Y_ions_intensity","extra_ions_names",
                                            "extra_ions_mass_offset","extra_ions_intensity","Rec"    
                                            ],inplace=True,errors="ignore")

                    ### reordered how this works so that all the conversions are done in-loop instead of once the whole sheet has been concatenated
                    ### this seems to run faster than concatenating everything and then doing conversions

                    #convert glycan_composition column entries to format from fragger-glyco
                    convert_dict={"H":"Hex","N":"HexNAc","F":"Fuc","S":"NeuAc","G":"NeuGc"}
                    glycanlist=parquet["glycan_composition"].tolist()
                    glycanlist_updated=[]
                    glycanlist_ambiguous=[]
                    for i,entry in enumerate(glycanlist):
                        if entry is None or entry=="unidentified":
                            glycanlist_updated.append(np.nan)
                            glycanlist_ambiguous.append(np.nan)
                        else:
                            if "," in entry:
                                entry=entry.split(",")[0]
                                glycanlist_ambiguous.append(True)
                            else:
                                glycanlist_ambiguous.append(False)
                            entrylist=list(entry)
                            newglycanentry=[]
                            for ele in entrylist:
                                if ele.isnumeric()==True:
                                    newglycanentry.append("("+ele+")")
                                else:
                                    newglycanentry.append(convert_dict[ele])
                            glycanlist_updated.append("".join(newglycanentry))
                    parquet["Total Glycan Composition"]=glycanlist_updated
                    parquet["Ambiguous Glycan ID"]=glycanlist_ambiguous

                    #unpack protein_list column
                    proteinlist=parquet["protein_list"].str.split(";").tolist()

                    truthlist=[]
                    for entry in proteinlist:
                        if "Reverse" not in entry[0] and "contaminant" not in str(entry):
                            truthlist.append(True)
                        else:
                            truthlist.append(False)
                    parquet=parquet[truthlist]

                    proteingroups=[]
                    proteinnames=[]
                    proteinlist_column=parquet["protein_list"].tolist()
                    for item in proteinlist_column:
                        if item.count(";")==0:
                            templist=item.split("|")
                            proteingroups.append(templist[1])
                            proteinnames.append(templist[2])
                        else:
                            proteingroups_torejoin=[]
                            proteinnames_torejoin=[]
                            for entry in item.split(";"):
                                templist=entry.split("|")
                                proteingroups_torejoin.append(templist[1])
                                proteinnames_torejoin.append(templist[2])
                            proteingroups.append(";".join(proteingroups_torejoin))
                            proteinnames.append(";".join(proteinnames_torejoin))

                    parquet["PG.ProteinGroups"]=proteingroups
                    parquet["PG.ProteinNames"]=proteinnames
                    parquet.drop(columns=["protein_list"],inplace=True)

                    #make EG.ModifiedPeptide column
                    parquet["ptms"]=parquet["ptms"].astype(str)
                    parquet["ptms"]=parquet["ptms"].replace({
                            "203.079373":"-HexNAc (N)",
                            "42.010565":"Acetyl (Protein N-term)",
                            "57.021464":"Carbamidomethyl (C)",
                            "79.966331":"Phospho (STY)",
                            "15.994915":"Oxidation (M)"},regex=True)
                    parquet["ptm_locations"]=parquet["ptm_locations"].astype(str)
                    parquet["ptm_locations"]=parquet["ptm_locations"].str.replace("[]","-1").str.replace("[","").str.replace("]","")

                    modifiedpeptides=[]
                    for i,entry in enumerate(parquet["ptm_locations"]):
                        if entry=="-1":
                            modifiedpeptides.append(parquet["PEP.StrippedSequence"].tolist()[i])
                        else:
                            str_to_list=list(parquet["PEP.StrippedSequence"].tolist()[i])
                            if len(parquet["ptm_locations"].tolist()[i])==1:
                                mod_loc=int(parquet["ptm_locations"].tolist()[i])+1
                                mod_add=parquet["ptms"].tolist()[i]
                                str_to_list.insert(mod_loc,mod_add)
                                modifiedpeptides.append("".join(str_to_list))
                            #if theres >1 ptm, we need to reformat some strings so we can insert them in the sequence
                            else:
                                ptmlocs=parquet["ptm_locations"].tolist()[i].strip().split(" ")
                                ptms=parquet["ptms"].tolist()[i].replace("[","").replace("]","").replace(") ","),").replace("\n ",",").split(",")
                                for ele in ptmlocs:
                                    if ele=="":
                                        ptmlocs.remove(ele)
                                ptms_for_loop=[]
                                for ele in ptms:
                                    ptms_for_loop.append("["+ele+"]")
                                for j,loc in enumerate(ptmlocs):
                                    mod_loc=int(loc)+j+1
                                    mod_add=ptms_for_loop[j]
                                    str_to_list.insert(mod_loc,mod_add)
                                modifiedpeptides.append("".join(str_to_list))
                    parquet["EG.ModifiedPeptide"]=modifiedpeptides
                    parquet=parquet.drop(columns=["ptms","ptm_locations"])

                    searchoutput=pd.concat([searchoutput,parquet],ignore_index=True)

                searchoutput.insert(1,"R.Condition","")
                searchoutput.insert(2,"R.Replicate","")
        
        #for DIA-NN 2.0 input
        if ".parquet" in input.searchreport()[0]["name"]:
            if len(input.searchreport())>1:
                searchoutput=pd.DataFrame()
                for i in range(len(input.searchreport())):
                    run=pd.read_parquet(input.searchreport()[i]["datapath"])
                    searchoutput=pd.concat([searchoutput,run])
            else:
                searchoutput=pd.read_parquet(input.searchreport()[0]["datapath"])
            if input.software()=="diann2.0":
                searchoutput.rename(columns={"Run":"R.FileName"},inplace=True)
                searchoutput.insert(1,"R.Condition","")
                searchoutput.insert(2,"R.Replicate","")
                searchoutput["EG.PeakWidth"]=searchoutput["RT.Stop"]-searchoutput["RT.Start"]

                if input.diann_mbr_switch()==False:
                    searchoutput=searchoutput[searchoutput["Protein.Q.Value"]<=0.01]
                if input.diann_mbr_switch()==True:
                    searchoutput=searchoutput[searchoutput["Global.PG.Q.Value"]<=0.01]

                searchoutput.rename(columns={"Modified.Sequence":"EG.ModifiedPeptide",
                                            "Stripped.Sequence":"PEP.StrippedSequence",
                                            "Precursor.Charge":"FG.Charge",
                                            "Precursor.Mz":"FG.PrecMz",
                                            "Protein.Group":"PG.ProteinGroups",
                                            "Protein.Names":"PG.ProteinNames",
                                            "Genes":"PG.Genes",
                                            "RT":"EG.ApexRT",
                                            "IM":"EG.IonMobility",
                                            "Precursor.Quantity":"FG.MS2Quantity",
                                            "PG.MaxLFQ":"PG.MS2Quantity"
                                            },inplace=True)

                searchoutput.drop(columns=["Run.Index","Channel","Precursor.Id","Precursor.Lib.Index","Decoy",
                                        "Proteotypic","Protein.Ids","iRT","Predicted.RT","Predicted.iRT",
                                        "iIM","Predicted.IM","Predicted.iIM","Precursor.Normalised",
                                        "Ms1.Area","Ms1.Normalised","Ms1.Apex.Area","Ms1.Apex.Mz.Delta",
                                        "Normalisation.Factor","Quantity.Quality","Empirical.Quality",
                                        "Normalisation.Noise","Ms1.Profile.Corr","Evidence","Mass.Evidence",
                                        "Channel.Evidence","Ms1.Total.Signal.Before","Ms1.Total.Signal.After",
                                        "RT.Start","RT.Stop","FWHM","PG.TopN","PG.MaxLFQ","Genes.TopN",
                                        "Genes.MaxLFQ","Genes.MaxLFQ.Unique","PG.MaxLFQ.Quality",
                                        "Genes.MaxLFQ.Quality","Genes.MaxLFQ.Unique.Quality","Q.Value",
                                        "PEP","Global.Q.Value","Lib.Q.Value","Peptidoform.Q.Value",
                                        "Global.Peptidoform.Q.Value","Lib.Peptidoform.Q.Value",
                                        "PTM.Site.Confidence","Site.Occupancy.Probabilities","Protein.Sites",
                                        "Lib.PTM.Site.Confidence","Translated.Q.Value","Channel.Q.Value",
                                        "PG.Q.Value","PG.PEP","GG.Q.Value","Lib.PG.Q.Value"
                                        ],inplace=True,errors="ignore")
                    
                searchoutput["EG.ModifiedPeptide"]=searchoutput["EG.ModifiedPeptide"].str.replace("(","[")
                searchoutput["EG.ModifiedPeptide"]=searchoutput["EG.ModifiedPeptide"].str.replace(")","]")
                searchoutput["EG.ModifiedPeptide"]=searchoutput["EG.ModifiedPeptide"].replace({
                        "UniMod:1":"Acetyl (Protein N-term)",
                        "UniMod:4":"Carbamidomethyl (C)",
                        "UniMod:21":"Phospho (STY)",
                        "UniMod:35":"Oxidation (M)"},regex=True)

        #this line is needed for some files since some will order the search report by file name and others won't. Need to account for this
        searchoutput=searchoutput.sort_values('R.FileName')

        return searchoutput
    
    #upload filled out metadata table
    @reactive.calc
    def inputmetadata():
        if input.metadata_upload() is None:
            metadata=pd.DataFrame(columns=["R.FileName","R.Condition","R.Replicate","remove"])
            return metadata
        else:
            metadata=pd.read_csv(input.metadata_upload()[0]["datapath"],sep=",")
        return metadata

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
                metadata=pd.DataFrame(columns=["R.FileName","R.Condition","R.Replicate","remove"])
                return render.DataGrid(metadata,width="100%")
            metadata=pd.DataFrame(searchoutput[["R.FileName","R.Condition","R.Replicate"]]).drop_duplicates().reset_index(drop=True)
            metadata["remove"]=metadata.apply(lambda _: '', axis=1)

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
            return "Use the Shiny report format when exporting search results to a .tsv file."
        if input.software()=="diann":
            return "Use the report.tsv file as the file input."
        if input.software()=="diann2.0":
            return "Use the report.parquet file as the file input."
        if input.software()=="ddalibrary":
            return "DDA libraries have limited functionality, can only plot ID metrics."
        if input.software()=="fragpipe":
            return "Use the psm.tsv file as the file input."
        if input.software()=="fragpipe_glyco":
            return "Use the psm.tsv file as the file input. Use the Glycoproteomics tab for processing."
        if input.software()=="bps_timsrescore":
            return "Use the .zip file from the artefacts download."
        if input.software()=="bps_timsdiann":
            return "Use the .zip file from the artefacts download."
        if input.software()=="bps_denovo":
            return "Use the .zip file from the artefacts download."
        if input.software()=="glycoscape":
            return "Use the .zip file from the artefacts download. Use the Glycoproteomics tab for processing."

    #download metadata table as shown
    @render.download(filename="metadata_"+str(date.today())+".csv")
    def metadata_download():
        metadata=metadata_table.data_view()
        metadata_condition=metadata_condition_table.data_view()

        orderlist=[]
        concentrationlist=[]
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
                searchoutput["Concentration"]=searchoutput["Concentration"].astype(float)
            else:
                searchoutput.insert(3,"Concentration",list(itertools.chain(*concentrationlist)))
                searchoutput["Concentration"]=searchoutput["Concentration"].astype(float)

        return searchoutput

    #switch for if MBR was used in DIANN, chaanges how we'll filter for Q value
    @render.ui
    def diann_mbr_ui():
        if input.software()=="diann" or input.software()=="diann2.0":
            return ui.input_switch("diann_mbr_switch","MBR used in DIA-NN? (Filter Protein.Q.Value if off, filter Global.PG.Q.Value if on)",value=False,width="700px")

#endregion

# ============================================================================= Settings
#region
    # ====================================== Color Settings
    #show color options as plots
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
    #matplotlib color options (plot_colortable)
    def matplotlibcolors():
        return plot_colortable(mcolors.TABLEAU_COLORS, ncols=1, sort_colors=False)
    #CSS color options (plot_colortable)
    @render.plot(width=800,height=800)
    def csscolors():
        return plot_colortable(mcolors.CSS4_COLORS)
    #render the color grids as images instead of plotting them explicitly
    @render.image
    def matplotcolors_image():
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        cwd=os.getcwd()
        foldername="images"
        joined=[cwd,foldername]
        matplotcolors_imagefile="\\".join([cwd,"images","matplotlib_tabcolors.png"])        
        img: ImgData={"src":matplotcolors_imagefile}
        return img
    @render.image
    def csscolors_image():
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
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
    #show a table of the sample conditions 
    @render.table()
    def customcolors_table1():
        try:
            searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
            conditioncolordf1=pd.DataFrame({"Condition":sampleconditions})
            return conditioncolordf1
        except:
            conditioncolordf1=pd.DataFrame({"Condition":[]})
            return conditioncolordf1

    #add an empty table header to match the conditions table
    @render.table
    def conditioncolors():
        conditioncolors_table=pd.DataFrame({"Color per run":[]})
        return conditioncolors_table
    #added a variable to help make sure that the rectangles that are shown for the color choices line up roughly with the table of sample conditions
    @render.ui
    def colorplot_height():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
        height=40*numconditions
        return ui.input_numeric("colorplot_height_input","Color per run height mod *no touchy >:(*",value=height)
    #plot rectangles in line with the sample conditions they'll be associated with in downstream plotting
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

    # ====================================== File Stats
    #stats about the input file
    @render.table
    def filestats():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()

        variablenames=["# samples","# conditions","Conditions","Replicates per Condition"]
        variablecalls=[numsamples,numconditions,sampleconditions,repspercondition]

        filestatsdf=pd.DataFrame({"Property":variablenames,"Values":variablecalls})
        
        return filestatsdf

    # ====================================== Column Check
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
                in_report.append("FALSE")
        columncheck_df=pd.DataFrame({"Expected Column":expectedcolumns,"in_report":in_report})
        columncheck_df["Needed?"]=["Yes","Yes","","Yes","Yes","","Yes","Yes","Yes","Yes","Yes","","Yes","","","Yes","Yes","Yes","Yes","","Yes","","","","Yes"]
        return columncheck_df

    # ====================================== File Preview
    #preview of searchoutput table
    @render.data_frame
    def filepreview():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
        return render.DataGrid(searchoutput,editable=False,width="100%")
 
    # ====================================== Extra Colors
    @render.image
    def brukercolors():
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        cwd=os.getcwd()
        foldername="images"
        joined=[cwd,foldername]
        brukercolors_imagefile="\\".join([cwd,"images","bruker_colors.png"])        
        img: ImgData={"src":brukercolors_imagefile}
        return img
#endregion  

# ============================================================================= ID Counts
#region

    # ====================================== Counts per Condition
    #plot ID metrics
    @reactive.effect
    def _():
        if input.idplotinput()=="all":
            @render.plot(width=input.idmetrics_width(),height=input.idmetrics_height())
            def idmetricsplot():
                resultdf,averagedf=idmetrics()
                idmetricscolor=replicatecolors()
                titlefont=input.titlefont()
                axisfont=input.axisfont()
                labelfont=input.labelfont()
                y_padding=input.ypadding()

                fig,ax=plt.subplots(nrows=2,ncols=2,sharex=True)
                fig.set_tight_layout(True)
                ax1=ax[0,0]
                ax2=ax[0,1]
                ax3=ax[1,0]
                ax4=ax[1,1]

                resultdf.plot.bar(ax=ax1,x="Cond_Rep",y="proteins",legend=False,width=0.8,color=idmetricscolor,edgecolor="k")
                ax1.bar_label(ax1.containers[0],label_type="edge",rotation=90,padding=5,fontsize=labelfont)
                ax1.set_ylim(top=max(resultdf["proteins"].tolist())+y_padding*max(resultdf["proteins"].tolist()))
                ax1.set_title("Protein Groups",fontsize=titlefont)

                resultdf.plot.bar(ax=ax2,x="Cond_Rep",y="proteins2pepts",legend=False,width=0.8,color=idmetricscolor,edgecolor="k")
                ax2.bar_label(ax2.containers[0],label_type="edge",rotation=90,padding=5,fontsize=labelfont)
                ax2.set_ylim(top=max(resultdf["proteins2pepts"].tolist())+y_padding*max(resultdf["proteins2pepts"].tolist()))
                ax2.set_title("Protein Groups with >2 Peptides",fontsize=titlefont)

                resultdf.plot.bar(ax=ax3,x="Cond_Rep",y="peptides",legend=False,width=0.8,color=idmetricscolor,edgecolor="k")
                ax3.bar_label(ax3.containers[0],label_type="edge",rotation=90,padding=5,fontsize=labelfont)
                ax3.set_ylim(top=max(resultdf["peptides"].tolist())+(y_padding+0.1)*max(resultdf["peptides"].tolist()))
                ax3.set_title("Peptides",fontsize=titlefont)
                ax3.set_xlabel("Condition",fontsize=axisfont)
                ax3.tick_params(axis="x",labelsize=axisfont,rotation=input.xaxis_label_rotation())

                resultdf.plot.bar(ax=ax4,x="Cond_Rep",y="precursors",legend=False,width=0.8,color=idmetricscolor,edgecolor="k")
                ax4.bar_label(ax4.containers[0],label_type="edge",rotation=90,padding=5,fontsize=labelfont)
                ax4.set_ylim(top=max(resultdf["precursors"].tolist())+(y_padding+0.1)*max(resultdf["precursors"].tolist()))
                ax4.set_title("Precursors",fontsize=titlefont)
                ax4.set_xlabel("Condition",fontsize=axisfont)
                ax4.tick_params(axis="x",labelsize=axisfont,rotation=input.xaxis_label_rotation())

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
                ax.tick_params(axis="y",labelsize=axisfont)
                ax.tick_params(axis="x",labelsize=axisfont,rotation=input.xaxis_label_rotation())
                ax.set_axisbelow(True)
                ax.grid(linestyle="--")

    # ====================================== Average Counts
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
                ax3.tick_params(axis='x',labelsize=axisfont,rotation=input.xaxis_label_rotation())
                ax3.set_xlabel("Condition",fontsize=axisfont)
                ax3.set_ylabel("  ",fontsize=axisfont)

                bars4=ax4.bar(averagedf["R.Condition"],averagedf["precursors_avg"],yerr=averagedf["precursors_stdev"],edgecolor="k",capsize=10,color=avgmetricscolor)
                ax4.bar_label(bars4,label_type="edge",rotation=90,padding=10,fontsize=labelfont)
                ax4.set_ylim(top=max(averagedf["precursors_avg"].tolist())+y_padding*max(averagedf["precursors_avg"].tolist()))
                ax4.set_title("Precursors",fontsize=titlefont)
                ax4.tick_params(axis='y',labelsize=axisfont)
                ax4.tick_params(axis='x',labelsize=axisfont,rotation=input.xaxis_label_rotation())
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
                ax.tick_params(axis='x',labelsize=axisfont,rotation=input.xaxis_label_rotation())
                ax.set_axisbelow(True)
                ax.grid(linestyle="--")

    # ====================================== CV Plots
    #plot cv violin plots
    @reactive.effect
    def _():
        @render.plot(width=input.cvplot_width(),height=input.cvplot_height())
        def cvplot():
            searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
            cvcalc_df=cvcalc()

            violincolors=colorpicker()

            titlefont=input.titlefont()
            axisfont=input.axisfont()

            cvplotinput=input.proteins_precursors_cvplot()
            cutoff95=input.removetop5percent()

            x=np.arange(len(cvcalc_df["R.Condition"]))

            fig,ax=plt.subplots()

            lineprops=dict(linestyle="--",color="black")
            flierprops=dict(markersize=3)

            if cutoff95==True:
                bplot=ax.boxplot(cvcalc_df[cvplotinput+" 95% CVs"],medianprops=lineprops,flierprops=flierprops)
                plot=ax.violinplot(cvcalc_df[cvplotinput+" 95% CVs"],showextrema=False)
                ax.set_title(cvplotinput+" CVs, 95% Cutoff",fontsize=titlefont)

            elif cutoff95==False:
                bplot=ax.boxplot(cvcalc_df[cvplotinput+" CVs"],medianprops=lineprops,flierprops=flierprops)
                plot=ax.violinplot(cvcalc_df[cvplotinput+" CVs"],showextrema=False)
                ax.set_title(cvplotinput+" CVs",fontsize=titlefont)

            ax.set_xticks(x+1,labels=cvcalc_df["R.Condition"],fontsize=axisfont,rotation=input.xaxis_label_rotation())
            ax.tick_params(axis="y",labelsize=axisfont)
            ax.set_ylabel("CV%",fontsize=axisfont)
            ax.set_xlabel("Condition",fontsize=axisfont)
            ax.grid(linestyle="--")
            ax.set_axisbelow(True)

            ax.axhline(y=20,color="black",linestyle="--")

            if numconditions==1:
                for z in plot["bodies"]:
                    z.set_facecolor(violincolors)
                    z.set_edgecolor("black")
                    z.set_alpha(0.7)
            else:
                for z,color in zip(plot["bodies"],violincolors):
                    z.set_facecolor(color)
                    z.set_edgecolor("black")
                    z.set_alpha(0.7)
    #show a table of mean/median CV values per condition 
    @render.table
    def cv_table():
        cvcalc_df=cvcalc()

        cvplotinput=input.proteins_precursors_cvplot()
        cutoff95=input.removetop5percent()

        cvtable_protein=pd.DataFrame()
        cvtable_precursor=pd.DataFrame()
        cvtable_peptide=pd.DataFrame()

        protein_meanlist=[]
        protein_medianlist=[]
        protein_meanlist95=[]
        protein_medianlist95=[]
        for run in cvcalc_df["R.Condition"]:
            protein_meanlist.append(np.mean(cvcalc_df[cvcalc_df["R.Condition"]==run]["Protein CVs"].tolist()))
            protein_meanlist95.append(np.mean(cvcalc_df[cvcalc_df["R.Condition"]==run]["Protein 95% CVs"].tolist()))
            protein_medianlist.append(np.median(cvcalc_df[cvcalc_df["R.Condition"]==run]["Protein CVs"].tolist()))
            protein_medianlist95.append(np.median(cvcalc_df[cvcalc_df["R.Condition"]==run]["Protein 95% CVs"].tolist()))
        cvtable_protein["R.Condition"]=cvcalc_df["R.Condition"]
        cvtable_protein["Protein Mean CVs"]=protein_meanlist
        cvtable_protein["Protein Mean CVs 95%"]=protein_meanlist95
        cvtable_protein["Protein Median CVs"]=protein_medianlist
        cvtable_protein["Protein Median CVs 95%"]=protein_medianlist95

        precursor_meanlist=[]
        precursor_medianlist=[]
        precursor_meanlist95=[]
        precursor_medianlist95=[]
        for run in cvcalc_df["R.Condition"]:
            precursor_meanlist.append(np.mean(cvcalc_df[cvcalc_df["R.Condition"]==run]["Precursor CVs"].tolist()))
            precursor_meanlist95.append(np.mean(cvcalc_df[cvcalc_df["R.Condition"]==run]["Precursor 95% CVs"].tolist()))
            precursor_medianlist.append(np.median(cvcalc_df[cvcalc_df["R.Condition"]==run]["Precursor CVs"].tolist()))
            precursor_medianlist95.append(np.median(cvcalc_df[cvcalc_df["R.Condition"]==run]["Precursor 95% CVs"].tolist()))
        cvtable_precursor["R.Condition"]=cvcalc_df["R.Condition"]
        cvtable_precursor["Precursor Mean CVs"]=precursor_meanlist
        cvtable_precursor["Precursor Mean CVs 95%"]=precursor_meanlist95
        cvtable_precursor["Precursor Median CVs"]=precursor_medianlist
        cvtable_precursor["Precursor Median CVs 95%"]=precursor_medianlist95         

        peptide_meanlist=[]
        peptide_medianlist=[]
        peptide_meanlist95=[]
        peptide_medianlist95=[]
        for run in cvcalc_df["R.Condition"]:
            peptide_meanlist.append(np.mean(cvcalc_df[cvcalc_df["R.Condition"]==run]["Peptide CVs"].tolist()))
            peptide_meanlist95.append(np.mean(cvcalc_df[cvcalc_df["R.Condition"]==run]["Peptide 95% CVs"].tolist()))
            peptide_medianlist.append(np.median(cvcalc_df[cvcalc_df["R.Condition"]==run]["Peptide CVs"].tolist()))
            peptide_medianlist95.append(np.median(cvcalc_df[cvcalc_df["R.Condition"]==run]["Peptide 95% CVs"].tolist()))
        cvtable_peptide["R.Condition"]=cvcalc_df["R.Condition"]
        cvtable_peptide["Peptide Mean CVs"]=peptide_meanlist
        cvtable_peptide["Peptide Mean CVs 95%"]=peptide_meanlist95
        cvtable_peptide["Peptide Median CVs"]=peptide_medianlist
        cvtable_peptide["Peptide Median CVs 95%"]=peptide_medianlist95  

        if cvplotinput=="Protein":
            if cutoff95==True:
                return cvtable_protein[["R.Condition","Protein Mean CVs 95%","Protein Median CVs 95%"]]
            if cutoff95==False:
                return cvtable_protein[["R.Condition","Protein Mean CVs","Protein Median CVs"]]
        if cvplotinput=="Precursor":
            if cutoff95==True:
                return cvtable_precursor[["R.Condition","Precursor Mean CVs 95%","Precursor Median CVs 95%"]]
            if cutoff95==False:
                return cvtable_precursor[["R.Condition","Precursor Mean CVs","Precursor Median CVs"]]
        if cvplotinput=="Peptide":
            if cutoff95==True:
                return cvtable_peptide[["R.Condition","Peptide Mean CVs 95%","Peptide Median CVs 95%"]]
            if cutoff95==False:
                return cvtable_peptide[["R.Condition","Peptide Mean CVs","Peptide Median CVs"]]

    # ====================================== IDs with CV Cutoff
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
            ax.set_xticks(x+width,cvcalc_df["R.Condition"],fontsize=axisfont,rotation=input.xaxis_label_rotation())
            ax.tick_params(axis="y",labelsize=axisfont)
            ax.set_xlabel("Condition",fontsize=axisfont)
            ax.set_ylabel("Counts",fontsize=axisfont)
            if cvinput=="proteins":
                ax.set_title("Protein Counts with CV Cutoffs",fontsize=titlefont)
            if cvinput=="precursors":
                ax.set_title("Precursor Counts with CV Cutoffs",fontsize=titlefont)
            if cvinput=="peptides":
                ax.set_title("Peptide Counts with CV Cutoffs",fontsize=titlefont)
            ax.set_axisbelow(True)
            ax.grid(linestyle="--")
    
    # ====================================== UpSet Plot
    @render.ui
    def specific_condition_ui():
        if input.upset_condition_or_run()=="specific_condition":
            searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
            opts=sampleconditions
            return ui.input_selectize("specific_condition_pick","Pick sample condition",choices=opts)
    @render.data_frame
    def upsetplot_counts():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
        if input.protein_precursor_pick()=="Protein":
            proteindict=dict()
            if input.upset_condition_or_run()=="condition":
                if numconditions==1:
                    for run in resultdf["Cond_Rep"].tolist():
                        proteinlist=searchoutput[searchoutput["Cond_Rep"]==run][["Cond_Rep","PG.ProteinGroups"]].drop_duplicates().reset_index(drop=True).drop(columns=["Cond_Rep"])
                        proteinlist.rename(columns={"PG.ProteinGroups":run},inplace=True)
                        proteindict[run]=proteinlist[run].tolist()
                else:
                    for condition in sampleconditions:
                        proteinlist=searchoutput[searchoutput["R.Condition"]==condition][["R.Condition","PG.ProteinGroups"]].drop_duplicates().reset_index(drop=True).drop(columns=["R.Condition"])
                        proteinlist.rename(columns={"PG.ProteinGroups":condition},inplace=True)
                        proteindict[condition]=proteinlist[condition].tolist()
                proteins=from_contents(proteindict)
            if input.upset_condition_or_run()=="individual":
                for run in resultdf["Cond_Rep"].tolist():
                    proteinlist=searchoutput[searchoutput["Cond_Rep"]==run][["Cond_Rep","PG.ProteinGroups"]].drop_duplicates().reset_index(drop=True).drop(columns=["Cond_Rep"])
                    proteinlist.rename(columns={"PG.ProteinGroups":run},inplace=True)
                    proteindict[run]=proteinlist[run].tolist()
                proteins=from_contents(proteindict)
            if input.upset_condition_or_run()=="specific_condition":
                df=searchoutput[searchoutput["R.Condition"]==input.specific_condition_pick()]
                for run in df["Cond_Rep"].drop_duplicates():
                    proteinlist=df[df["Cond_Rep"]==run][["Cond_Rep","PG.ProteinGroups"]].drop_duplicates().reset_index(drop=True).drop(columns=["Cond_Rep"])
                    proteinlist.rename(columns={"PG.ProteinGroups":run},inplace=True)
                    proteindict[run]=proteinlist[run].tolist()
                proteins=from_contents(proteindict)
            plottingdf=proteins
            titlemod="Protein"

        elif input.protein_precursor_pick()=="Peptide":
            peptidedict=dict()
            if input.upset_condition_or_run()=="condition":
                if numconditions==1:
                    for run in resultdf["Cond_Rep"].tolist():
                        peptidelist=searchoutput[searchoutput["Cond_Rep"]==run][["Cond_Rep","EG.ModifiedPeptide"]].drop_duplicates().reset_index(drop=True).drop(columns=["Cond_Rep"])
                        peptidelist.rename(columns={"EG.ModifiedPeptide":run},inplace=True)
                        peptidedict[run]=peptidelist[run].tolist()
                else:
                    for condition in sampleconditions:
                        peptidelist=searchoutput[searchoutput["R.Condition"]==condition][["R.Condition","EG.ModifiedPeptide"]].drop_duplicates().reset_index(drop=True).drop(columns=["R.Condition"])
                        peptidelist.rename(columns={"EG.ModifiedPeptide":condition},inplace=True)
                        peptidedict[condition]=peptidelist[condition].tolist()
                peptides=from_contents(peptidedict)
            if input.upset_condition_or_run()=="individual":
                for run in resultdf["Cond_Rep"].tolist():
                    peptidelist=searchoutput[searchoutput["Cond_Rep"]==run][["Cond_Rep","EG.ModifiedPeptide"]].drop_duplicates().reset_index(drop=True).drop(columns=["Cond_Rep"])
                    peptidelist.rename(columns={"EG.ModifiedPeptide":run},inplace=True)
                    peptidedict[run]=peptidelist[run].tolist()
                peptides=from_contents(peptidedict)
            if input.upset_condition_or_run()=="specific_condition":
                df=searchoutput[searchoutput["R.Condition"]==input.specific_condition_pick()]
                for run in df["Cond_Rep"].drop_duplicates():
                    peptidelist=df[df["Cond_Rep"]==run][["Cond_Rep","EG.ModifiedPeptide"]].drop_duplicates().reset_index(drop=True).drop(columns=["Cond_Rep"])
                    peptidelist.rename(columns={"EG.ModifiedPeptide":run},inplace=True)
                    peptidedict[run]=peptidelist[run].tolist()
                peptides=from_contents(peptidedict)
            plottingdf=peptides
            titlemod="Peptide"
        elif input.protein_precursor_pick()=="Precursor":
            searchoutput["pep_charge"]=searchoutput["EG.ModifiedPeptide"]+searchoutput["FG.Charge"].astype(str)

            peptidedict=dict()
            if input.upset_condition_or_run()=="condition":
                if numconditions==1:
                    for run in resultdf["Cond_Rep"].tolist():
                        peptidelist=searchoutput[searchoutput["Cond_Rep"]==run][["Cond_Rep","pep_charge"]].drop_duplicates().reset_index(drop=True).drop(columns=["Cond_Rep"])
                        peptidelist.rename(columns={"pep_charge":run},inplace=True)
                        peptidedict[run]=peptidelist[run].tolist()
                else:
                    for condition in sampleconditions:
                        peptidelist=searchoutput[searchoutput["R.Condition"]==condition][["R.Condition","pep_charge"]].drop_duplicates().reset_index(drop=True).drop(columns=["R.Condition"])
                        peptidelist.rename(columns={"pep_charge":condition},inplace=True)
                        peptidedict[condition]=peptidelist[condition].tolist()
                peptides=from_contents(peptidedict)
            if input.upset_condition_or_run()=="individual":
                for run in resultdf["Cond_Rep"].tolist():
                    peptidelist=searchoutput[searchoutput["Cond_Rep"]==run][["Cond_Rep","pep_charge"]].drop_duplicates().reset_index(drop=True).drop(columns=["Cond_Rep"])
                    peptidelist.rename(columns={"pep_charge":run},inplace=True)
                    peptidedict[run]=peptidelist[run].tolist()
                peptides=from_contents(peptidedict)
            if input.upset_condition_or_run()=="specific_condition":
                df=searchoutput[searchoutput["R.Condition"]==input.specific_condition_pick()]
                for run in df["Cond_Rep"].drop_duplicates():
                    peptidelist=df[df["Cond_Rep"]==run][["Cond_Rep","pep_charge"]].drop_duplicates().reset_index(drop=True).drop(columns=["Cond_Rep"])
                    peptidelist.rename(columns={"pep_charge":run},inplace=True)
                    peptidedict[run]=peptidelist[run].tolist()
                peptides=from_contents(peptidedict)
            plottingdf=peptides
            titlemod="Precursor"

        countsperrun=query(plottingdf).category_totals
        totalcounts=query(plottingdf,max_degree=1).total
        subset1_df=pd.DataFrame(query(plottingdf,max_degree=1).subset_sizes).reset_index()
        subset_nminus1_df=pd.DataFrame(query(plottingdf,min_degree=len(countsperrun)-1).subset_sizes).reset_index()

        str1="Total unique "+titlemod+"s across all runs"
        str2=titlemod+"s found in only 1 run"
        str3=titlemod+"s found in at least "+str(len(countsperrun)-1)+" out of "+str(len(countsperrun))+" runs"
        labellist=[str1,str2,str3]
        countlist=[totalcounts,sum(subset1_df["size"]),sum(subset_nminus1_df["size"])]
        df=pd.DataFrame({"Property":labellist,"Counts":countlist})

        return render.DataGrid(df,editable=False,width="600px",filters=False)
    #plot upset plot
    @reactive.effect
    def _():
        @render.plot(width=input.upsetplot_width(),height=input.upsetplot_height())
        def upsetplot():
            searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
            if input.protein_precursor_pick()=="Protein":
                proteindict=dict()
                if input.upset_condition_or_run()=="condition":
                    if numconditions==1:
                        for run in resultdf["Cond_Rep"].tolist():
                            proteinlist=searchoutput[searchoutput["Cond_Rep"]==run][["Cond_Rep","PG.ProteinGroups"]].drop_duplicates().reset_index(drop=True).drop(columns=["Cond_Rep"])
                            proteinlist.rename(columns={"PG.ProteinGroups":run},inplace=True)
                            proteindict[run]=proteinlist[run].tolist()
                    else:
                        for condition in sampleconditions:
                            proteinlist=searchoutput[searchoutput["R.Condition"]==condition][["R.Condition","PG.ProteinGroups"]].drop_duplicates().reset_index(drop=True).drop(columns=["R.Condition"])
                            proteinlist.rename(columns={"PG.ProteinGroups":condition},inplace=True)
                            proteindict[condition]=proteinlist[condition].tolist()
                    proteins=from_contents(proteindict)
                if input.upset_condition_or_run()=="individual":
                    for run in resultdf["Cond_Rep"].tolist():
                        proteinlist=searchoutput[searchoutput["Cond_Rep"]==run][["Cond_Rep","PG.ProteinGroups"]].drop_duplicates().reset_index(drop=True).drop(columns=["Cond_Rep"])
                        proteinlist.rename(columns={"PG.ProteinGroups":run},inplace=True)
                        proteindict[run]=proteinlist[run].tolist()
                    proteins=from_contents(proteindict)
                if input.upset_condition_or_run()=="specific_condition":
                    df=searchoutput[searchoutput["R.Condition"]==input.specific_condition_pick()]
                    for run in df["Cond_Rep"].drop_duplicates():
                        proteinlist=df[df["Cond_Rep"]==run][["Cond_Rep","PG.ProteinGroups"]].drop_duplicates().reset_index(drop=True).drop(columns=["Cond_Rep"])
                        proteinlist.rename(columns={"PG.ProteinGroups":run},inplace=True)
                        proteindict[run]=proteinlist[run].tolist()
                    proteins=from_contents(proteindict)
                plottingdf=proteins
                titlemod="Protein"
                min_degree=len(proteindict)-1

            elif input.protein_precursor_pick()=="Peptide":
                peptidedict=dict()
                if input.upset_condition_or_run()=="condition":
                    if numconditions==1:
                        for run in resultdf["Cond_Rep"].tolist():
                            peptidelist=searchoutput[searchoutput["Cond_Rep"]==run][["Cond_Rep","EG.ModifiedPeptide"]].drop_duplicates().reset_index(drop=True).drop(columns=["Cond_Rep"])
                            peptidelist.rename(columns={"EG.ModifiedPeptide":run},inplace=True)
                            peptidedict[run]=peptidelist[run].tolist()
                    else:
                        for condition in sampleconditions:
                            peptidelist=searchoutput[searchoutput["R.Condition"]==condition][["R.Condition","EG.ModifiedPeptide"]].drop_duplicates().reset_index(drop=True).drop(columns=["R.Condition"])
                            peptidelist.rename(columns={"EG.ModifiedPeptide":condition},inplace=True)
                            peptidedict[condition]=peptidelist[condition].tolist()
                    peptides=from_contents(peptidedict)
                if input.upset_condition_or_run()=="individual":
                    for run in resultdf["Cond_Rep"].tolist():
                        peptidelist=searchoutput[searchoutput["Cond_Rep"]==run][["Cond_Rep","EG.ModifiedPeptide"]].drop_duplicates().reset_index(drop=True).drop(columns=["Cond_Rep"])
                        peptidelist.rename(columns={"EG.ModifiedPeptide":run},inplace=True)
                        peptidedict[run]=peptidelist[run].tolist()
                    peptides=from_contents(peptidedict)
                if input.upset_condition_or_run()=="specific_condition":
                    df=searchoutput[searchoutput["R.Condition"]==input.specific_condition_pick()]
                    for run in df["Cond_Rep"].drop_duplicates():
                        peptidelist=df[df["Cond_Rep"]==run][["Cond_Rep","EG.ModifiedPeptide"]].drop_duplicates().reset_index(drop=True).drop(columns=["Cond_Rep"])
                        peptidelist.rename(columns={"EG.ModifiedPeptide":run},inplace=True)
                        peptidedict[run]=peptidelist[run].tolist()
                    peptides=from_contents(peptidedict)
                plottingdf=peptides
                titlemod="Peptide"
                min_degree=len(peptidedict)-1

            elif input.protein_precursor_pick()=="Precursor":
                searchoutput["pep_charge"]=searchoutput["EG.ModifiedPeptide"]+searchoutput["FG.Charge"].astype(str)
                peptidedict=dict()
                if input.upset_condition_or_run()=="condition":
                    if numconditions==1:
                        for run in resultdf["Cond_Rep"].tolist():
                            peptidelist=searchoutput[searchoutput["Cond_Rep"]==run][["Cond_Rep","pep_charge"]].drop_duplicates().reset_index(drop=True).drop(columns=["Cond_Rep"])
                            peptidelist.rename(columns={"pep_charge":run},inplace=True)
                            peptidedict[run]=peptidelist[run].tolist()
                    else:
                        for condition in sampleconditions:
                            peptidelist=searchoutput[searchoutput["R.Condition"]==condition][["R.Condition","pep_charge"]].drop_duplicates().reset_index(drop=True).drop(columns=["R.Condition"])
                            peptidelist.rename(columns={"pep_charge":condition},inplace=True)
                            peptidedict[condition]=peptidelist[condition].tolist()
                    peptides=from_contents(peptidedict)
                if input.upset_condition_or_run()=="individual":
                    for run in resultdf["Cond_Rep"].tolist():
                        peptidelist=searchoutput[searchoutput["Cond_Rep"]==run][["Cond_Rep","pep_charge"]].drop_duplicates().reset_index(drop=True).drop(columns=["Cond_Rep"])
                        peptidelist.rename(columns={"pep_charge":run},inplace=True)
                        peptidedict[run]=peptidelist[run].tolist()
                    peptides=from_contents(peptidedict)
                if input.upset_condition_or_run()=="specific_condition":
                    df=searchoutput[searchoutput["R.Condition"]==input.specific_condition_pick()]
                    for run in df["Cond_Rep"].drop_duplicates():
                        peptidelist=df[df["Cond_Rep"]==run][["Cond_Rep","pep_charge"]].drop_duplicates().reset_index(drop=True).drop(columns=["Cond_Rep"])
                        peptidelist.rename(columns={"pep_charge":run},inplace=True)
                        peptidedict[run]=peptidelist[run].tolist()
                    peptides=from_contents(peptidedict)
                plottingdf=peptides
                titlemod="Precursor"
                min_degree=len(peptidedict)-1

            fig=plt.figure()
            if input.upsetfilter()=="nofilter":
                upset=UpSet(plottingdf,show_counts=True,sort_by="cardinality").plot(fig)
            if input.upsetfilter()=="1run":
                upset=UpSet(plottingdf,show_counts=True,sort_by="cardinality",max_degree=1).plot(fig)
            if input.upsetfilter()=="n-1runs":
                upset=UpSet(plottingdf,show_counts=True,sort_by="cardinality",min_degree=min_degree).plot(fig)
            
            upset["totals"].set_title("# "+titlemod+"s")
            plt.ylabel(titlemod+" Intersections",fontsize=14)

    # ====================================== UpSet Plot (stats)
    #render ui call for dropdown calling sample condition names
    @render.ui
    def upsetplotstats_conditionlist_ui():
        if input.upsetplotstats_whattoplot()=="condition" or input.upsetplotstats_whattoplot()=="specific_condition":
            searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
            opts=sampleconditions
            return ui.input_selectize("upsetplotstats_conditionlist_pick","Pick sample condition",choices=opts)
    @reactive.effect
    def _():
        @render.plot(width=input.upsetplotstats_width(),height=input.upsetplotstats_height())
        def upsetplotstats_singlehitIDplot():
            searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()

            axisfont=input.axisfont()
            titlefont=input.titlefont()
            legendfont=input.legendfont()

            if input.upsetplotstats_peptide_precursor()=="Peptide":
                peptidedict=dict()
                if input.upsetplotstats_whattoplot()=="individual":
                    for run in resultdf["Cond_Rep"].tolist():
                        peptidelist=searchoutput[searchoutput["Cond_Rep"]==run][["Cond_Rep","EG.ModifiedPeptide"]].drop_duplicates().reset_index(drop=True).drop(columns=["Cond_Rep"])
                        peptidelist.rename(columns={"EG.ModifiedPeptide":run},inplace=True)
                        peptidedict[run]=peptidelist[run].tolist()
                    peptides=from_contents(peptidedict)
                if input.upsetplotstats_whattoplot()=="condition" or input.upsetplotstats_whattoplot()=="specific_condition":
                    df=searchoutput[searchoutput["R.Condition"]==input.upsetplotstats_conditionlist_pick()]
                    for run in df["Cond_Rep"].drop_duplicates():
                        peptidelist=df[df["Cond_Rep"]==run][["Cond_Rep","EG.ModifiedPeptide"]].drop_duplicates().reset_index(drop=True).drop(columns=["Cond_Rep"])
                        peptidelist.rename(columns={"EG.ModifiedPeptide":run},inplace=True)
                        peptidedict[run]=peptidelist[run].tolist()
                    peptides=from_contents(peptidedict)
                plottingdf=peptides
                setindex="EG.ModifiedPeptide"
            if input.upsetplotstats_peptide_precursor()=="Precursor":
                searchoutput["pep_charge"]=searchoutput["EG.ModifiedPeptide"]+searchoutput["FG.Charge"].astype(str)
                peptidedict=dict()
                if input.upsetplotstats_whattoplot()=="individual":
                    for run in resultdf["Cond_Rep"].tolist():
                        peptidelist=searchoutput[searchoutput["Cond_Rep"]==run][["Cond_Rep","pep_charge"]].drop_duplicates().reset_index(drop=True).drop(columns=["Cond_Rep"])
                        peptidelist.rename(columns={"pep_charge":run},inplace=True)
                        peptidedict[run]=peptidelist[run].tolist()
                    peptides=from_contents(peptidedict)
                if input.upsetplotstats_whattoplot()=="condition" or input.upsetplotstats_whattoplot()=="specific_condition":
                    df=searchoutput[searchoutput["R.Condition"]==input.upsetplotstats_conditionlist_pick()]
                    for run in df["Cond_Rep"].drop_duplicates():
                        peptidelist=df[df["Cond_Rep"]==run][["Cond_Rep","pep_charge"]].drop_duplicates().reset_index(drop=True).drop(columns=["Cond_Rep"])
                        peptidelist.rename(columns={"pep_charge":run},inplace=True)
                        peptidedict[run]=peptidelist[run].tolist()
                    peptides=from_contents(peptidedict)
                plottingdf=peptides
                setindex="pep_charge"
            
            IDs_1run=pd.DataFrame(query(plottingdf,max_degree=1).data).reset_index()
            if input.upsetplotstats_whattoplot()=="condition" or input.upsetplotstats_whattoplot()=="specific_condition":
                searchoutput_pepindex=searchoutput[searchoutput["R.Condition"]==input.upsetplotstats_conditionlist_pick()].set_index(setindex)
            else:
                searchoutput_pepindex=searchoutput.set_index(setindex)
            IDs_1run_searchoutput=searchoutput_pepindex.loc[IDs_1run["id"]]

            if input.upsetplotstats_whattoplot()=="individual" or input.upsetplotstats_whattoplot()=="condition":
                #pull mz and IM from every ID
                remainderIDs=searchoutput[["FG.PrecMz","EG.IonMobility"]].drop_duplicates()
                scatterlabel="All IDs"
            if input.upsetplotstats_whattoplot()=="specific_condition":
                #pull mz and IM from every ID from specified condition
                remainderIDs=searchoutput[searchoutput["R.Condition"]==input.upsetplotstats_conditionlist_pick()][["FG.PrecMz","EG.IonMobility"]].drop_duplicates()
                scatterlabel="All IDs from selected condition"
            if input.upsetplotstats_plottype()=="scatter":
                fig,ax=plt.subplots()
                #scatter of all IDs
                ax.scatter(remainderIDs["FG.PrecMz"],remainderIDs["EG.IonMobility"],zorder=1,s=2,label=scatterlabel)
                #scatter of just the single run hits
                ax.scatter(IDs_1run_searchoutput["FG.PrecMz"],IDs_1run_searchoutput["EG.IonMobility"],zorder=2,s=2,label="IDs in only 1 Run")
                ax.set_xlabel("m/z",fontsize=axisfont)
                ax.set_ylabel("Ion Mobility ($1/K_{0}$)",fontsize=axisfont)
                ax.legend(markerscale=5)
                ax.set_axisbelow(True)
                ax.grid(linestyle="--")

            if input.upsetplotstats_plottype()=="2dhist":
                numbins=[100,100]
                cmap=matplotlib.colors.LinearSegmentedColormap.from_list("",["white","blue","red"])
                
                fig,ax=plt.subplots(ncols=2,sharey=True,sharex=True)
                
                j=ax[0].hist2d(remainderIDs["FG.PrecMz"],remainderIDs["EG.IonMobility"],bins=numbins,cmap=cmap)
                k=ax[1].hist2d(IDs_1run_searchoutput["FG.PrecMz"],IDs_1run_searchoutput["EG.IonMobility"],bins=numbins,cmap=cmap)

                ax[0].set_xlabel("m/z",fontsize=axisfont)
                ax[1].set_xlabel("m/z",fontsize=axisfont)
                ax[0].set_ylabel("Ion Mobility ($1/K_{0}$)",fontsize=axisfont)
                ax[1].tick_params("y",labelleft=True)
                fig.colorbar(j[3],ax=ax[0])
                fig.colorbar(k[3],ax=ax[1])
                fig.set_tight_layout(True)
                ax[0].set_title("All IDs")
                ax[1].set_title("Unique IDs")

    # ====================================== Tracker
    #render table of detected proteins and their average PG.MS2Quantity
    @render.data_frame
    def protein_df():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
        df=searchoutput[["PG.ProteinGroups","PG.MS2Quantity"]].groupby("PG.ProteinGroups").mean().reset_index().rename(columns={"PG.MS2Quantity":"Mean_PG.MS2Quantity"})
        return render.DataGrid(df,width="100%",selection_mode="row",editable=False)
    #render table of peptides identified for picked protein from above table
    @render.data_frame
    def pickedprotein_df():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
        if len(protein_df.data_view(selected=True)["PG.ProteinGroups"].tolist())==0:
            df=pd.DataFrame()
            return render.DataGrid(df)
        else:
            selectedprotein=protein_df.data_view(selected=True)["PG.ProteinGroups"].tolist()[0]
            #df=searchoutput[searchoutput["PG.ProteinGroups"]==selectedprotein][["Cond_Rep","PEP.StrippedSequence","EG.ModifiedPeptide","FG.Charge","FG.MS2Quantity"]].drop_duplicates()
            df=searchoutput[searchoutput["PG.ProteinGroups"]==selectedprotein][["PEP.StrippedSequence"]].drop_duplicates().sort_values("PEP.StrippedSequence")
            return render.DataGrid(df,width="100%",selection_mode="row")
    #line plot of either protein or peptide signal depending on what is selected in the above two tables
    @reactive.effect
    def _():
        @render.plot(width=input.tracker_width(),height=input.tracker_height())
        def tracker_plot():
            searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()

            axisfont=input.axisfont()
            titlefont=input.titlefont()

            #show empty graph since nothing was selected
            if len(protein_df.data_view(selected=True)["PG.ProteinGroups"].tolist())==0:
                fig,ax=plt.subplots()
            #if just protien is selected, show protein intensities across runs
            elif len(pickedprotein_df.data_view(selected=True)["PEP.StrippedSequence"].tolist())==0:
                fig,ax=plt.subplots()
                selectedprotein=protein_df.data_view(selected=True)["PG.ProteinGroups"].tolist()[0]
                plottingdf=searchoutput[searchoutput["PG.ProteinGroups"]==selectedprotein][["Cond_Rep","PG.MS2Quantity"]].drop_duplicates().fillna(0)
                if len(plottingdf)<len(searchoutput["Cond_Rep"].drop_duplicates().reset_index(drop=True)):
                    expectedrows=pd.DataFrame({"Cond_Rep":searchoutput["Cond_Rep"].drop_duplicates().reset_index(drop=True)})
                    plottingdf=expectedrows.merge(plottingdf,how="left",left_on="Cond_Rep",right_on="Cond_Rep").fillna(0)
                ax.plot(plottingdf["Cond_Rep"],plottingdf["PG.MS2Quantity"],marker="o")
                if str(selectedprotein).count(";")>=1:
                    selectedprotein=str(selectedprotein).split(";")[0]
                ax.set_title(str(selectedprotein),fontsize=titlefont)
            #show intensity for selected peptide from selected protein across runs
            else:
                selectedprotein=protein_df.data_view(selected=True)["PG.ProteinGroups"].tolist()[0]
                proteindf=searchoutput[searchoutput["PG.ProteinGroups"]==selectedprotein][["Cond_Rep","PEP.StrippedSequence","EG.ModifiedPeptide","FG.Charge","FG.MS2Quantity"]].drop_duplicates()

                selectedpeptide=pickedprotein_df.data_view(selected=True)["PEP.StrippedSequence"].tolist()[0]
                peptidedf=proteindf[proteindf["PEP.StrippedSequence"]==selectedpeptide]

                modpeps=peptidedf["EG.ModifiedPeptide"].drop_duplicates().tolist()

                fig,ax=plt.subplots()
                for pep in modpeps:
                    chargelist=peptidedf[peptidedf["EG.ModifiedPeptide"]==pep]["FG.Charge"].drop_duplicates().tolist()
                    for charge in chargelist:
                        plottingdf=peptidedf[(peptidedf["EG.ModifiedPeptide"]==pep)&(peptidedf["FG.Charge"]==charge)]
                        if len(plottingdf)<len(searchoutput["Cond_Rep"].drop_duplicates().reset_index(drop=True)):
                            expectedrows=pd.DataFrame({"Cond_Rep":searchoutput["Cond_Rep"].drop_duplicates().reset_index(drop=True)})
                            plottingdf=expectedrows.merge(plottingdf,how="left",left_on="Cond_Rep",right_on="Cond_Rep").fillna(0)
                        else:
                            pass
                        ax.plot(plottingdf["Cond_Rep"],plottingdf["FG.MS2Quantity"],marker="o",label=pep.strip("_")+"_"+str(charge)+"+")

                ax.legend(loc='center left', bbox_to_anchor=(1,0.5))
                if str(selectedprotein).count(";")>=1:
                    selectedprotein=str(selectedprotein).split(";")[0]
                ax.set_title(str(selectedprotein)+"_"+str(selectedpeptide),fontsize=titlefont)

            ax.tick_params(axis="x",rotation=input.xaxis_label_rotation())
            ax.set_xlabel("Condition",fontsize=axisfont)
            ax.set_ylabel("MS2 Intensity",fontsize=axisfont)
            ax.set_axisbelow(True)
            ax.grid(linestyle="--")
   
#endregion

# ============================================================================= Metrics
#region
    # ====================================== Charge State
    #plot charge states
    @reactive.effect
    def _():
        @render.plot(width=input.chargestate_width(),height=input.chargestate_height())
        def chargestateplot():
            searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
            titlefont=input.titlefont()
            axisfont=input.axisfont()
            labelfont=input.labelfont()
            y_padding=input.ypadding()
        
            chargestatedf_condition,chargestatedf_run=chargestates()
            if input.chargestate_condition_or_run()=="condition":
                plottingdf=chargestatedf_condition
                chargestatecolor=colorpicker()
            if input.chargestate_condition_or_run()=="individual":
                plottingdf=chargestatedf_run
                chargestatecolor=replicatecolors()

            #plot as stacked bar graphs 
            if input.chargestate_stacked()==True:
                fig,ax=plt.subplots()
                matplottabcolors=list(mcolors.TABLEAU_COLORS)
                x=np.arange(len(plottingdf))
                for i in range(len(plottingdf)):
                    charges=list(set(plottingdf["Charge States"][i]))
                    frequencies=[len(list(group)) for key, group in groupby(sorted(plottingdf["Charge States"][i]))]
                    totals=sum(frequencies)
                    bottom=np.zeros(len(frequencies))
                    for y,ele in enumerate(frequencies):
                        frequencies[y]=round((ele/totals)*100,1)
                    for z in range(len(charges)):
                        ax.bar(x[i],frequencies[z],bottom=bottom,color=matplottabcolors[z],width=0.75)
                        bottom+=frequencies[z]
                ax.legend(charges,loc="center left",bbox_to_anchor=(1, 0.5))
                ax.set_xticks(x,labels=plottingdf["Sample Names"],rotation=input.xaxis_label_rotation())
                ax.set_ylim(top=105)
                ax.set_ylabel("Frequency (%)",fontsize=axisfont)
                ax.set_xlabel("Condition",fontsize=axisfont)
                ax.set_axisbelow(True)
                ax.grid(linestyle="--")

            #show as regular bar graphs in separate subplots
            else:
                #condition for when there's only a single sample in searchoutput
                if len(plottingdf)==1:
                    fig,ax=plt.subplots()
                    x=list(set(plottingdf["Charge States"][0]))
                    frequencies=[len(list(group)) for key, group in groupby(sorted(plottingdf["Charge States"][0]))]
                    
                    totals=sum(frequencies)
                    for y,ele in enumerate(frequencies):
                        frequencies[y]=round((ele/totals)*100,1)
                    ax.bar(x,frequencies,edgecolor="k",color=chargestatecolor)
                    ax.set_title(plottingdf["Sample Names"][0],fontsize=titlefont)
                    ax.set_axisbelow(True)
                    ax.grid(linestyle="--")
                    ax.bar_label(ax.containers[0],label_type="edge",padding=10,rotation=90,fontsize=labelfont)

                    ax.set_ylim(bottom=-5,top=max(frequencies)+y_padding*max(frequencies))
                    ax.tick_params(axis="both",labelsize=axisfont)
                    ax.set_xticks(np.arange(1,max(x)+1,1))
                    ax.set_xlabel("Charge State",fontsize=axisfont)             
                    ax.set_ylabel("Frequency (%)",fontsize=axisfont)
                #for when there's more than a single sample in searchoutput
                else:
                    fig,ax=plt.subplots(nrows=1,ncols=len(plottingdf))
                    for i in range(len(plottingdf)):
                        x=list(set(plottingdf["Charge States"][i]))
                        frequencies=[len(list(group)) for key, group in groupby(sorted(plottingdf["Charge States"][i]))]

                        totals=sum(frequencies)
                        for y,ele in enumerate(frequencies):
                            frequencies[y]=round((ele/totals)*100,1)
                        #check if there's only one sample condition, the loop will try and split the color name/code which will result in an error
                        if numconditions==1:
                            ax[i].bar(x,frequencies,color=chargestatecolor,edgecolor="k")
                        else:
                            ax[i].bar(x,frequencies,color=chargestatecolor[i],edgecolor="k")
                        ax[i].set_title(plottingdf["Sample Names"][i],fontsize=titlefont)
                        ax[i].set_axisbelow(True)
                        ax[i].grid(linestyle="--")
                        ax[i].bar_label(ax[i].containers[0],label_type="edge",padding=10,rotation=90,fontsize=labelfont)

                        ax[i].set_ylim(bottom=-5,top=max(frequencies)+y_padding*max(frequencies))
                        ax[i].tick_params(axis="both",labelsize=axisfont)
                        ax[i].set_xticks(np.arange(1,max(x)+1,1))
                        ax[i].set_xlabel("Charge State",fontsize=axisfont)
                    ax[0].set_ylabel("Frequency (%)",fontsize=axisfont)
                fig.set_tight_layout(True)

    # ====================================== Peptide Length
    #ui call for dropdown for marking peptide lengths
    @render.ui
    def lengthmark_ui():
        if input.peplengthinput()=="barplot":
            minlength=7
            maxlength=30
            opts=[item for item in range(minlength,maxlength+1)]
            opts.insert(0,0)
            return ui.column(4,ui.input_switch("hide_lengthmark","Hide peptide length marker"),ui.input_selectize("lengthmark_pick","Pick peptide length to mark on bar plot (use 0 for maximum)",choices=opts))
    #plot peptide legnths
    @reactive.effect
    def _():
        @render.plot(width=input.peptidelength_width(),height=input.peptidelength_height())
        def peptidelengthplot():
            searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
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
                        if numconditions==1:
                            ax.plot(x,frequencies,color=colors,linewidth=2)
                        else:
                            ax.plot(x,frequencies,color=colors[i],linewidth=2)
                        legendlist.append(plottingdf["Sample Names"][i])
                ax.tick_params(axis="both",labelsize=axisfont)
                ax.set_xlabel("Peptide Length",fontsize=axisfont)
                ax.set_ylabel("Counts",fontsize=axisfont)
                ax.set_axisbelow(True)
                ax.grid(linestyle="--")
                ax.legend(legendlist,fontsize=legendfont)

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
                    if input.hide_lengthmark()==False:
                        if lengthmark!=0:
                            ax.vlines(x=x[lengthmark-min(x)],ymin=frequencies[lengthmark-min(x)],ymax=frequencies[lengthmark-min(x)]+0.2*frequencies[lengthmark-min(x)],color="k")
                            ax.text(x=x[lengthmark-min(x)],y=frequencies[lengthmark-min(x)]+0.2*frequencies[lengthmark-min(x)],s=str(x[lengthmark-min(x)])+": "+str(frequencies[lengthmark-min(x)]),fontsize=labelfont)
                        if lengthmark==0:
                            ax.vlines(x=x[np.argmax(frequencies)],ymin=max(frequencies),ymax=max(frequencies)+0.2*max(frequencies),color="k")
                            ax.text(x=x[np.argmax(frequencies)],y=max(frequencies)+0.2*max(frequencies),s=str(x[np.argmax(frequencies)])+": "+str(max(frequencies)),fontsize=labelfont)
                            ax.set_ylim(top=max(frequencies)+y_padding*max(frequencies))
                    ax.tick_params(axis="both",labelsize=axisfont)
                    ax.set_xlabel("Peptide Length",fontsize=axisfont)
                    ax.set_ylabel("Counts",fontsize=axisfont)
                    ax.xaxis.set_minor_locator(MultipleLocator(1))
                else:
                    fig,ax=plt.subplots(nrows=1,ncols=len(plottingdf),figsize=(15,5))
                    for i in range(len(plottingdf)):
                        x=list(set(plottingdf["Peptide Lengths"][i]))
                        frequencies=[len(list(group)) for key, group in groupby(sorted(plottingdf["Peptide Lengths"][i]))]
                        if numconditions==1:
                            ax[i].bar(x,frequencies,color=colors,edgecolor="k")
                        else:
                            ax[i].bar(x,frequencies,color=colors[i],edgecolor="k")
                        ax[i].set_title(plottingdf["Sample Names"][i],fontsize=titlefont)
                        ax[i].set_axisbelow(True)
                        ax[i].grid(linestyle="--")
                        if input.hide_lengthmark()==False:
                            if lengthmark!=0:
                                ax[i].vlines(x=x[lengthmark-min(x)],ymin=frequencies[lengthmark-min(x)],ymax=frequencies[lengthmark-min(x)]+0.2*frequencies[lengthmark-min(x)],color="k")
                                ax[i].text(x=x[lengthmark-min(x)],y=frequencies[lengthmark-min(x)]+0.2*frequencies[lengthmark-min(x)],s=str(x[lengthmark-min(x)])+": "+str(frequencies[lengthmark-min(x)]),fontsize=labelfont)
                            if lengthmark==0:
                                ax[i].vlines(x=x[np.argmax(frequencies)],ymin=max(frequencies),ymax=max(frequencies)+0.2*max(frequencies),color="k")
                                ax[i].text(x=x[np.argmax(frequencies)],y=max(frequencies)+0.2*max(frequencies),s=str(x[np.argmax(frequencies)])+": "+str(max(frequencies)),fontsize=labelfont)
                                ax[i].set_ylim(top=max(frequencies)+y_padding*max(frequencies))
                        ax[i].tick_params(axis="both",labelsize=axisfont)
                        ax[i].set_xlabel("Peptide Length",fontsize=axisfont)
                        ax[i].xaxis.set_minor_locator(MultipleLocator(1))
                    ax[0].set_ylabel("Counts",fontsize=axisfont)
            fig.set_tight_layout(True)
    
    # ====================================== Peptides per Protein
    #plot peptides per protein
    @reactive.effect
    def _():
        @render.plot(width=input.pepsperprotein_width(),height=input.pepsperprotein_height())
        def pepsperproteinplot():
            searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
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
                        if numconditions==1:
                            ax.plot(x,frequencies,color=colors,linewidth=2)
                        else:
                            ax.plot(x,frequencies,color=colors[i],linewidth=2)
                        legendlist.append(plottingdf["Sample Names"][i])

                ax.set_xlim(left=0,right=input.pepsperprotein_xrange())
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
                        ax.set_xlim(left=0,right=input.pepsperprotein_xrange())
                else:
                    fig,ax=plt.subplots(nrows=1,ncols=len(plottingdf),figsize=(15,5))
                    for i in range(len(plottingdf)):
                        x=list(set(plottingdf["Peptides per Protein"][i]))
                        frequencies=[len(list(group)) for key, group in groupby(sorted(plottingdf["Peptides per Protein"][i]))]
                        if numconditions==1:
                            ax[i].bar(x,frequencies,color=colors)
                        else:
                            ax[i].bar(x,frequencies,color=colors[i])
                        ax[i].set_title(plottingdf["Sample Names"][i],fontsize=titlefont)
                        ax[i].set_axisbelow(True)
                        ax[i].grid(linestyle="--")

                        ax[i].tick_params(axis="both",labelsize=axisfont)
                        ax[i].set_xticks(np.arange(0,max(x)+1,25))
                        ax[i].set_xlabel("# Peptides",fontsize=axisfont)
                        ax[i].set_xlim(left=0,right=input.pepsperprotein_xrange())
                    ax[0].set_ylabel("Counts",fontsize=axisfont)
                fig.set_tight_layout(True)
    
    # ====================================== Dynamic Range
    #plot dynamic range
    @reactive.effect
    def _():
        @render.plot(width=input.dynamicrange_width(),height=input.dynamicrange_height())
        def dynamicrangeplot():
            conditioninput=input.conditionname()
            propertyinput=input.meanmedian()
            searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()

            markersize=25
            titlefont=input.titlefont()

            if propertyinput=="mean":
                intensitydf=searchoutput[searchoutput["R.Condition"]==conditioninput][["PG.ProteinGroups","PG.MS2Quantity"]].drop_duplicates().groupby("PG.ProteinGroups").mean().reset_index(drop=True)

            elif propertyinput=="median":
                intensitydf=searchoutput[searchoutput["R.Condition"]==conditioninput][["PG.ProteinGroups","PG.MS2Quantity"]].drop_duplicates().groupby("PG.ProteinGroups").median().reset_index(drop=True)

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
            intensitydf=searchoutput[searchoutput["R.Condition"]==conditioninput][["PG.ProteinGroups","PG.MS2Quantity"]].drop_duplicates().groupby("PG.ProteinGroups").mean().reset_index()
        elif propertyinput=="median":
            intensitydf=searchoutput[searchoutput["R.Condition"]==conditioninput][["PG.ProteinGroups","PG.MS2Quantity"]].drop_duplicates().groupby("PG.ProteinGroups").median().reset_index()
        intensitydf=intensitydf.sort_values("PG.MS2Quantity",ascending=False).reset_index(drop=True)

        return render.DataGrid(intensitydf.iloc[:input.top_n()],editable=False)

    # ====================================== Mass Accuracy
    @render.ui
    def massaccuracy_bins_ui():
        if input.massaccuracy_violin_hist()=="histogram":
            return ui.input_slider("massaccuracy_hist_bins","Number of bins",min=10,max=200,value=100,step=10,ticks=True,width="300px")
    #plot mass accuracy
    @reactive.effect
    def _():
        @render.plot(width=input.massaccuracy_width(),height=input.massaccuracy_height())
        def massaccuracy_plot():
            searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
            massaccuracy_df=pd.DataFrame()
            massaccuracy_df["Cond_Rep"]=searchoutput["Cond_Rep"].drop_duplicates().reset_index(drop=True)
            massaccuracy=[]
            for run in searchoutput["Cond_Rep"].drop_duplicates().tolist():
                massaccuracylist=searchoutput[searchoutput["Cond_Rep"]==run]["FG.CalibratedMassAccuracy (PPM)"].dropna().tolist()
                massaccuracy.append(massaccuracylist)

            massaccuracy_df["Mass Accuracy"]=massaccuracy

            violincolors=replicatecolors()
            titlefont=input.titlefont()
            axisfont=input.axisfont()
            labelfont=input.labelfont()

            if input.massaccuracy_violin_hist()=="violin":
                fig,ax=plt.subplots()
                medianlineprops=dict(linestyle="--",color="black")
                flierprops=dict(markersize=3)
                x=np.arange(len(massaccuracy_df["Cond_Rep"].tolist()))
                plot=ax.violinplot(massaccuracy_df["Mass Accuracy"],showextrema=False)
                ax.boxplot(massaccuracy_df["Mass Accuracy"],medianprops=medianlineprops,flierprops=flierprops)
                ax.set_ylabel("Mass Accuracy (ppm)",fontsize=axisfont)
                ax.set_xlabel("Run",fontsize=axisfont)
                ax.set_xticks(x+1,labels=massaccuracy_df["Cond_Rep"].tolist(),rotation=input.xaxis_label_rotation())
                ax.grid(linestyle="--")
                ax.set_axisbelow(True)

                if numconditions==1:
                    for z in plot["bodies"]:
                        z.set_facecolor(violincolors)
                        z.set_edgecolor("black")
                        z.set_alpha(0.7)
                else:
                    for z,color in zip(plot["bodies"],violincolors):
                        z.set_facecolor(color)
                        z.set_edgecolor("black")
                        z.set_alpha(0.7)

            if input.massaccuracy_violin_hist()=="histogram":
                if numsamples==1:
                    fig,ax=plt.subplots()
                    ax.hist(massaccuracy_df["Mass Accuracy"],bins=input.massaccuracy_hist_bins(),color=violincolors)
                    ax.set_xlabel("Mass Accuracy (ppm)",fontsize=axisfont)
                    ax.set_ylabel("Frequency",fontsize=axisfont)
                    ax.set_title(run,fontsize=titlefont)
                    ax.grid(linestyle="--")
                    ax.set_axisbelow(True)
                else:
                    fig,ax=plt.subplots(ncols=len(massaccuracy_df["Cond_Rep"]))
                    for i,run in enumerate(massaccuracy_df["Cond_Rep"]):
                        if numconditions==1:
                            ax[i].hist(massaccuracy_df["Mass Accuracy"][i],bins=input.massaccuracy_hist_bins(),color=violincolors)
                        else:
                            ax[i].hist(massaccuracy_df["Mass Accuracy"][i],bins=input.massaccuracy_hist_bins(),color=violincolors[i])
                        ax[i].set_xlabel("Mass Accuracy (ppm)",fontsize=axisfont)
                        ax[i].set_title(run,fontsize=titlefont)
                        ax[i].grid(linestyle="--")
                        ax[i].set_axisbelow(True)
                    ax[0].set_ylabel("Frequency",fontsize=axisfont)

    # ====================================== Data Completeness
    #render ui call for dropdown calling sample condition names
    @render.ui
    def datacompleteness_sampleconditions_ui():
        if input.datacompleteness_sampleconditions_switch()==True:
            searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
            opts=sampleconditions
            return ui.input_selectize("datacompleteness_sampleconditions_pick","Pick sample condition",choices=opts)
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

            if input.datacompleteness_sampleconditions_switch()==True:
                plottingdf=searchoutput[searchoutput["R.Condition"]==input.datacompleteness_sampleconditions_pick()]
                if input.protein_peptide()=="proteins":
                    proteincounts=[len(list(group)) for key, group in groupby(sorted(plottingdf[["R.Condition","R.Replicate","PG.ProteinGroups"]].drop_duplicates().drop(columns=["R.Condition","R.Replicate"]).reset_index(drop=True).groupby(["PG.ProteinGroups"]).size().tolist()))]

                elif input.protein_peptide()=="peptides":
                    proteincounts=[len(list(group)) for key, group in groupby(sorted(plottingdf[["R.Condition","R.Replicate","EG.ModifiedPeptide"]].drop_duplicates().drop(columns=["R.Condition","R.Replicate"]).reset_index(drop=True).groupby(["EG.ModifiedPeptide"]).size().tolist()))]

                elif input.protein_peptide()=="strippedpeptides":
                    proteincounts=[len(list(group)) for key, group in groupby(sorted(plottingdf[["R.Condition","R.Replicate","PEP.StrippedSequence"]].drop_duplicates().drop(columns=["R.Condition","R.Replicate"]).reset_index(drop=True).groupby(["PEP.StrippedSequence"]).size().tolist()))]

            else:
                if input.protein_peptide()=="proteins":
                    proteincounts=[len(list(group)) for key, group in groupby(sorted(searchoutput[["R.Condition","R.Replicate","PG.ProteinGroups"]].drop_duplicates().drop(columns=["R.Condition","R.Replicate"]).reset_index(drop=True).groupby(["PG.ProteinGroups"]).size().tolist()))]

                elif input.protein_peptide()=="peptides":
                    proteincounts=[len(list(group)) for key, group in groupby(sorted(searchoutput[["R.Condition","R.Replicate","EG.ModifiedPeptide"]].drop_duplicates().drop(columns=["R.Condition","R.Replicate"]).reset_index(drop=True).groupby(["EG.ModifiedPeptide"]).size().tolist()))]

                elif input.protein_peptide()=="strippedpeptides":
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

    # ====================================== Peak Widths
    #plot peak widths
    @reactive.effect
    def _():
        @render.plot(width=input.peakwidth_width(),height=input.peakwidth_height())
        def peakwidthplot():
            searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()

            violincolors=replicatecolors()
            titlefont=input.titlefont()
            axisfont=input.axisfont()

            fwhm_df=peakwidths()

            x=np.arange(len(fwhm_df["Cond_Rep"].tolist()))
            fig,ax=plt.subplots()
            medianlineprops=dict(linestyle="--",color="black")
            flierprops=dict(markersize=3)
            if input.peakwidth_removetop5percent()==False:
                plot=ax.violinplot(fwhm_df["Peak Width"],showextrema=False)
                bplot=ax.boxplot(fwhm_df["Peak Width"],medianprops=medianlineprops,flierprops=flierprops)
            elif input.peakwidth_removetop5percent()==True:
                plot=ax.violinplot(fwhm_df["Peak Width 95%"],showextrema=False)
                bplot=ax.boxplot(fwhm_df["Peak Width 95%"],medianprops=medianlineprops,flierprops=flierprops)

            ax.set_ylabel("Peak Width (s)",fontsize=axisfont)
            ax.set_xlabel("Run",fontsize=axisfont)
            ax.set_xticks(x+1,labels=fwhm_df["Cond_Rep"].tolist(),rotation=input.xaxis_label_rotation())
            ax.grid(linestyle="--")
            ax.set_axisbelow(True)

            if numconditions==1:
                for z in plot["bodies"]:
                    z.set_facecolor(violincolors)
                    z.set_edgecolor("black")
                    z.set_alpha(0.7)
            else:
                for z,color in zip(plot["bodies"],violincolors):
                    z.set_facecolor(color)
                    z.set_edgecolor("black")
                    z.set_alpha(0.7)              
    #show a table of mean/median peak widths per run 
    @render.table
    def peakwidth_table():
            searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
            fwhm_df=peakwidths()
            peakwidthtable=pd.DataFrame()

            meanlist=[]
            medianlist=[]
            meanlist95=[]
            medianlist95=[]
            for run in fwhm_df["Cond_Rep"]:
                meanlist.append(np.mean(fwhm_df[fwhm_df["Cond_Rep"]==run]["Peak Width"].tolist()))
                meanlist95.append(np.mean(fwhm_df[fwhm_df["Cond_Rep"]==run]["Peak Width 95%"].tolist()))
                medianlist.append(np.median(fwhm_df[fwhm_df["Cond_Rep"]==run]["Peak Width"].tolist()))
                medianlist95.append(np.median(fwhm_df[fwhm_df["Cond_Rep"]==run]["Peak Width 95%"].tolist()))

            peakwidthtable["Run"]=fwhm_df["Cond_Rep"]
            peakwidthtable["Mean Peak Width (s)"]=meanlist
            peakwidthtable["Median Peak Width (s)"]=medianlist
            peakwidthtable["Mean Peak Width 95% (s)"]=meanlist95
            peakwidthtable["Median Peak Width 95% (s)"]=medianlist95

            if input.peakwidth_removetop5percent()==True:
                return peakwidthtable[["Run","Mean Peak Width 95% (s)","Median Peak Width 95% (s)"]]
            elif input.peakwidth_removetop5percent()==False:
                return peakwidthtable[["Run","Mean Peak Width (s)","Median Peak Width (s)"]]

    # ====================================== Missed Cleavages
    @reactive.effect
    def _():
        @render.plot(width=input.missedcleavages_width(),height=input.missedcleavages_height())
        def missedcleavages_plot():
            searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()

            enzyme_rules=input.enzyme_rules()
            missedcleavages=[]
            for pep in searchoutput["PEP.StrippedSequence"]:
                if enzyme_rules=="trypsin":
                    if pep.count("K")+pep.count("R")>1:
                        missedcleavages.append(pep.count("K")+pep.count("R")-1)
                    else:
                        missedcleavages.append(0)
            searchoutput["Missed Cleavages"]=missedcleavages

            missedcleavages_df=pd.DataFrame()
            for run in searchoutput["Cond_Rep"].drop_duplicates().tolist():
                df=pd.DataFrame(searchoutput[searchoutput["Cond_Rep"]==run]["Missed Cleavages"].value_counts().reset_index(drop=True)).transpose()
                missedcleavages_df=pd.concat([missedcleavages_df,df],axis=0)
            missedcleavages_df=missedcleavages_df.reset_index(drop=True)
            missedcleavages_df["Cond_Rep"]=searchoutput["Cond_Rep"].drop_duplicates().tolist()

            maxvalue=missedcleavages_df.select_dtypes(include=[np.number]).max()[0]
            x=np.arange(len(missedcleavages_df["Cond_Rep"].tolist()))

            width=input.missedcleavages_barwidth()
            y_padding=input.ypadding()
            titlefont=input.titlefont()
            axisfont=input.axisfont()
            labelfont=input.labelfont()
            legendfont=input.legendfont()

            fig,ax=plt.subplots()
            legend_patches=[]
            for i in range(len(missedcleavages_df.columns.tolist())-1):
                ax.bar(x+(i*width),missedcleavages_df[i],width=width,edgecolor="k")
                ax.bar_label(ax.containers[i],label_type="edge",rotation=90,padding=5,fontsize=labelfont)
                legend_patches.append(mpatches.Patch(color=list(mcolors.TABLEAU_COLORS.keys())[i],label=i))
            ax.set_ylim(top=maxvalue+(y_padding*maxvalue),bottom=-(0.025*maxvalue))
            ax.set_xticks(x+width,missedcleavages_df["Cond_Rep"].tolist(),rotation=input.xaxis_label_rotation())
            ax.legend(handles=legend_patches,loc="upper right",prop={"size":legendfont})
            ax.set_title("Missed Cleavages",fontsize=titlefont)
            ax.set_ylabel("Counts",fontsize=axisfont)
            ax.set_xlabel("Condition",fontsize=axisfont)
            ax.grid(linestyle="--")
            ax.set_axisbelow(True)

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
    #generate list to pull from to pick PTMs
    @render.ui
    def ptmlist_ui():
        listofptms=find_ptms()
        ptmshortened=[]
        for i in range(len(listofptms)):
            ptmshortened.append(re.sub(r'\(.*?\)',"",listofptms[i]))
        ptmdict={ptmshortened[i]: listofptms[i] for i in range(len(listofptms))}
        return ui.input_selectize("foundptms","Pick PTM to plot data for",choices=ptmdict,selected=listofptms[0])
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
        for i in searchoutput["Cond_Rep"].drop_duplicates().reset_index(drop=True):
            df=searchoutput[searchoutput["Cond_Rep"]==i][["R.Condition","R.Replicate","PG.ProteinGroups","EG.ModifiedPeptide","FG.Charge"]]
            if df.empty:
                continue
            #number of proteins with specified PTM
            numptmproteins.append(df[df["EG.ModifiedPeptide"].str.contains(ptm)]["PG.ProteinGroups"].nunique())

            #number of proteins with 2 peptides and specified PTM
            numptmproteins2pepts.append(len(df[df["EG.ModifiedPeptide"].str.contains(ptm)][["PG.ProteinGroups","EG.ModifiedPeptide"]].drop_duplicates().groupby("PG.ProteinGroups").size().reset_index(name="peptides").query("peptides>1")))

            #number of peptides with specified PTM
            numptmpeptides.append(df[df["EG.ModifiedPeptide"].str.contains(ptm)]["EG.ModifiedPeptide"].nunique())

            #number of precursors with specified PTM
            numptmprecursors.append(len(df[df["EG.ModifiedPeptide"].str.contains(ptm)][["EG.ModifiedPeptide","FG.Charge"]].drop_duplicates()))

        ptmresultdf=pd.DataFrame({"Cond_Rep":resultdf["Cond_Rep"],"proteins":numptmproteins,"proteins2pepts":numptmproteins2pepts,"peptides":numptmpeptides,"precursors":numptmprecursors})

        propcolumnlist=["proteins","proteins2pepts","peptides","precursors"]

        for column in propcolumnlist:
            exec(f'ptmresultdf["{column}_enrich%"]=round((ptmresultdf["{column}"]/resultdf["{column}"])*100,1)')
        return ptmresultdf,ptm
    #calculate CVs for selected PTM
    @reactive.calc
    def ptmcvs_calc():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
        resultdf,averagedf=idmetrics()
        ptmresultdf,ptm=ptmcounts()

        ptmcvs=pd.DataFrame()
        ptmcvs["R.Condition"]=averagedf["R.Condition"]
        proteincv=[]
        proteinptmcv95=[]
        precursorcv=[]
        precursorptmcv95=[]

        df=searchoutput[["R.Condition","R.Replicate","PG.ProteinGroups","PG.MS2Quantity","FG.Charge","EG.ModifiedPeptide","FG.MS2Quantity"]].drop_duplicates().reset_index(drop=True)
        for x,condition in enumerate(averagedf["R.Condition"]):
            ptmdf=df[df["R.Condition"]==condition][["R.Condition","R.Replicate","PG.ProteinGroups","PG.MS2Quantity","FG.Charge","EG.ModifiedPeptide","FG.MS2Quantity"]].drop_duplicates().reset_index(drop=True)
            
            if maxreplicatelist[x]==1:
                emptylist=[]
                proteincv.append(emptylist)
                proteinptmcv95.append(emptylist)
                precursorcv.append(emptylist)
                precursorptmcv95.append(emptylist)
            else:
                #protein CVs for specified PTMs
                mean=ptmdf[ptmdf["EG.ModifiedPeptide"].str.contains(ptm)!=False][["R.Condition","PG.ProteinGroups","PG.MS2Quantity"]].drop_duplicates().groupby(["R.Condition","PG.ProteinGroups"]).mean().rename(columns={"PG.MS2Quantity":"PTM Protein Mean"}).reset_index(drop=True)
                stdev=ptmdf[ptmdf["EG.ModifiedPeptide"].str.contains(ptm)!=False][["R.Condition","PG.ProteinGroups","PG.MS2Quantity"]].drop_duplicates().groupby(["R.Condition","PG.ProteinGroups"]).std().rename(columns={"PG.MS2Quantity":"PTM Protein Stdev"}).reset_index(drop=True)
                cvptmproteintable=pd.concat([mean,stdev],axis=1)
                cvptmproteintable["PTM CV"]=(cvptmproteintable["PTM Protein Stdev"]/cvptmproteintable["PTM Protein Mean"]*100).tolist()
                cvptmproteintable.drop(columns=["PTM Protein Mean","PTM Protein Stdev"],inplace=True)
                cvptmproteintable.dropna(inplace=True)
                cvptmproteintable=cvptmproteintable.loc[(cvptmproteintable!=0).any(axis=1)]
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
                cvptmprecursortable=cvptmprecursortable.loc[(cvptmprecursortable!=0).any(axis=1)]
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

        peptidecvlist=[]
        peptidecvlist95=[]
        for x,condition in enumerate(searchoutput["R.Condition"].drop_duplicates().tolist()):
            df=searchoutput[(searchoutput["R.Condition"]==condition)&(searchoutput["EG.ModifiedPeptide"].str.contains(ptm))]
            placeholderdf=pd.DataFrame()
            if maxreplicatelist[x]==1:
                emptylist=[]
                peptidecvlist.append(emptylist)
                peptidecvlist95.append(emptylist)
            else:
                for run in searchoutput["Cond_Rep"].drop_duplicates().tolist():
                    df1=df[df["Cond_Rep"]==run][["EG.ModifiedPeptide","FG.MS2Quantity"]].groupby("EG.ModifiedPeptide").head(3).groupby("EG.ModifiedPeptide").mean()
                    placeholderdf=pd.concat([placeholderdf,df1],axis=0)
                mean=placeholderdf.sort_values("EG.ModifiedPeptide").groupby("EG.ModifiedPeptide").mean()
                std=placeholderdf.sort_values("EG.ModifiedPeptide").groupby("EG.ModifiedPeptide").std()
                cv=(std/mean)*100
                cv=cv["FG.MS2Quantity"].dropna().tolist()
                peptidecvlist.append(cv)

                top95=np.percentile(cv,95)
                cvlist95=[]
                for i in cv:
                    if i <=top95:
                        cvlist95.append(i)
                peptidecvlist95.append(cvlist95)
            
        ptmcvs["Peptide CVs"]=peptidecvlist
        ptmcvs["Peptide 95% CVs"]=peptidecvlist95

        return ptmcvs

    # ====================================== Counts per Condition
    #plot PTM ID metrics
    @reactive.effect
    def _():
        plotinput=input.ptmidplotinput()
        ptmresultdf,ptm=ptmcounts()
        figsize=(15,10)
        titlefont=input.titlefont()
        axisfont=input.axisfont()
        labelfont=input.labelfont()
        y_padding=input.ypadding()
        idmetricscolor=replicatecolors()

        if input.ptm_counts_vs_enrich()=="counts":
            y1="proteins"
            y2="proteins2pepts"
            y3="peptides"
            y4="precursors"
            titlemod="ID Counts for PTM: "
            ylabel="Counts"
        if input.ptm_counts_vs_enrich()=="percent":
            y1="proteins_enrich%"
            y2="proteins2pepts_enrich%"
            y3="peptides_enrich%"
            y4="precursors_enrich%"
            titlemod="% of IDs for PTM: "
            ylabel="% of IDs"

        if plotinput=="all":
            @render.plot(width=input.ptmidmetrics_width(),height=input.ptmidmetrics_height())
            def ptmidmetricsplot():
                fig,ax=plt.subplots(nrows=2,ncols=2,figsize=figsize,sharex=True)
                fig.set_tight_layout(True)
                ax1=ax[0,0]
                ax2=ax[0,1]
                ax3=ax[1,0]
                ax4=ax[1,1]

                ptmresultdf.plot.bar(ax=ax1,x="Cond_Rep",y=y1,legend=False,width=0.8,color=idmetricscolor,edgecolor="k",fontsize=axisfont)
                ax1.bar_label(ax1.containers[0],label_type="edge",rotation=90,padding=5,fontsize=labelfont)
                ax1.set_ylim(top=max(ptmresultdf[y1].tolist())+y_padding*max(ptmresultdf[y1].tolist()))
                ax1.set_title("Protein Groups",fontsize=titlefont)

                ptmresultdf.plot.bar(ax=ax2,x="Cond_Rep",y=y2,legend=False,width=0.8,color=idmetricscolor,edgecolor="k",fontsize=axisfont)
                ax2.bar_label(ax2.containers[0],label_type="edge",rotation=90,padding=5,fontsize=labelfont)
                ax2.set_ylim(top=max(ptmresultdf[y2].tolist())+y_padding*max(ptmresultdf[y2].tolist()))
                ax2.set_title("Protein Groups with >2 Peptides",fontsize=titlefont)

                ptmresultdf.plot.bar(ax=ax3,x="Cond_Rep",y=y3,legend=False,width=0.8,color=idmetricscolor,edgecolor="k",fontsize=axisfont)
                ax3.bar_label(ax3.containers[0],label_type="edge",rotation=90,padding=5,fontsize=labelfont)
                ax3.set_ylim(top=max(ptmresultdf[y3].tolist())+(y_padding+0.1)*max(ptmresultdf[y3].tolist()))
                ax3.set_title("Peptides",fontsize=titlefont)
                ax3.set_xlabel("Condition",fontsize=axisfont)
                ax3.set_ylabel("  ",fontsize=axisfont)
                ax3.tick_params(axis="x",labelsize=axisfont,rotation=input.xaxis_label_rotation())

                ptmresultdf.plot.bar(ax=ax4,x="Cond_Rep",y=y4,legend=False,width=0.8,color=idmetricscolor,edgecolor="k",fontsize=axisfont)
                ax4.bar_label(ax4.containers[0],label_type="edge",rotation=90,padding=5,fontsize=labelfont)
                ax4.set_ylim(top=max(ptmresultdf[y4].tolist())+(y_padding+0.1)*max(ptmresultdf[y4].tolist()))
                ax4.set_title("Precursors",fontsize=titlefont)
                ax4.set_xlabel("Condition",fontsize=axisfont)
                ax4.tick_params(axis="x",labelsize=axisfont,rotation=input.xaxis_label_rotation())

                fig.text(0, 0.6,ylabel,ha="left",va="center",rotation="vertical",fontsize=axisfont)

                plt.suptitle(titlemod+ptm,y=1,fontsize=titlefont)

                ax1.set_axisbelow(True)
                ax1.grid(linestyle="--")
                ax2.set_axisbelow(True)
                ax2.grid(linestyle="--")
                ax3.set_axisbelow(True)
                ax3.grid(linestyle="--")
                ax4.set_axisbelow(True)
                ax4.grid(linestyle="--")
            
        else:
            @render.plot(width=input.ptmidmetrics_width(),height=input.ptmidmetrics_height())
            def ptmidmetricsplot():
                if plotinput=="proteins":
                    titleprop="Proteins"
                if plotinput=="proteins2pepts":
                    titleprop="Proteins with >2 Peptides"
                if plotinput=="peptides":
                    titleprop="Peptides"
                if plotinput=="precursors":
                    titleprop="Precursors"

                if input.ptm_counts_vs_enrich()=="counts":
                    y=plotinput
                if input.ptm_counts_vs_enrich()=="percent":
                    y=plotinput+"_enrich%"

                fig,ax=plt.subplots()
                ptmresultdf.plot.bar(ax=ax,x="Cond_Rep",y=y,legend=False,width=0.8,color=idmetricscolor,edgecolor="k")
                ax.bar_label(ax.containers[0],label_type="edge",rotation=90,padding=5,fontsize=labelfont)
                ax.set_ylim(top=max(ptmresultdf[y].tolist())+y_padding*max(ptmresultdf[y].tolist()))
                plt.ylabel(ylabel,fontsize=axisfont)
                plt.xlabel("Condition",fontsize=axisfont)
                plt.title(titleprop,fontsize=titlefont)
                ax.tick_params(axis="y",labelsize=axisfont)
                ax.tick_params(axis="x",labelsize=axisfont,rotation=input.xaxis_label_rotation())
                ax.set_axisbelow(True)
                ax.grid(linestyle="--")

                plt.suptitle(titlemod+ptm,y=1,fontsize=titlefont)

    # ====================================== CV Plots    
    #plot PTM CV violin plots
    @reactive.effect
    def _():
        @render.plot(width=input.ptmcvplot_width(),height=input.ptmcvplot_height())
        def ptm_cvplot():
            searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
            resultdf,averagedf=idmetrics()
            ptmresultdf,ptm=ptmcounts()
            ptmcvs=ptmcvs_calc()

            colors=colorpicker()
            cvplotinput=input.ptm_proteins_precursors()
            cutoff95=input.ptm_removetop5percent()
            
            titlefont=input.titlefont()
            axisfont=input.axisfont()

            n=len(sampleconditions)
            x=np.arange(n)

            fig,ax=plt.subplots()

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

            ax.set_xticks(x+1,labels=ptmcvs["R.Condition"],fontsize=axisfont,rotation=input.xaxis_label_rotation())
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
    #show a table of mean/median CV values per condition for selected PTM
    @render.table
    def ptm_cvtable():
        ptmcvs=ptmcvs_calc()

        ptmcvs_summary=pd.DataFrame()
        proteinptmcv_mean=[]
        proteinptmcv95_mean=[]
        precursorptmcv_mean=[]
        precursorptmcv95_mean=[]
        peptideptmcv_mean=[]
        peptideptmcv95_mean=[]

        proteinptmcv_median=[]
        proteinptmcv95_median=[]
        precursorptmcv_median=[]
        precursorptmcv95_median=[]
        peptideptmcv_median=[]
        peptideptmcv95_median=[]
        for i,run in enumerate(ptmcvs["R.Condition"].tolist()):
            proteinptmcv_mean.append(np.mean(ptmcvs[ptmcvs["R.Condition"]==run]["Protein CVs"][i]))
            proteinptmcv95_mean.append(np.mean(ptmcvs[ptmcvs["R.Condition"]==run]["Protein 95% CVs"][i]))
            
            precursorptmcv_mean.append(np.mean(ptmcvs[ptmcvs["R.Condition"]==run]["Precursor CVs"][i]))
            precursorptmcv95_mean.append(np.mean(ptmcvs[ptmcvs["R.Condition"]==run]["Precursor 95% CVs"][i]))

            peptideptmcv_mean.append(np.mean(ptmcvs[ptmcvs["R.Condition"]==run]["Peptide CVs"][i]))
            peptideptmcv95_mean.append(np.mean(ptmcvs[ptmcvs["R.Condition"]==run]["Peptide 95% CVs"][i]))
            
            proteinptmcv_median.append(np.median(ptmcvs[ptmcvs["R.Condition"]==run]["Protein CVs"][i]))
            proteinptmcv95_median.append(np.median(ptmcvs[ptmcvs["R.Condition"]==run]["Protein 95% CVs"][i]))
            
            precursorptmcv_median.append(np.median(ptmcvs[ptmcvs["R.Condition"]==run]["Precursor CVs"][i]))
            precursorptmcv95_median.append((np.median(ptmcvs[ptmcvs["R.Condition"]==run]["Precursor 95% CVs"][i])))
            
            peptideptmcv_median.append(np.median(ptmcvs[ptmcvs["R.Condition"]==run]["Peptide CVs"][i]))
            peptideptmcv95_median.append((np.median(ptmcvs[ptmcvs["R.Condition"]==run]["Peptide 95% CVs"][i])))
        
        ptmcvs_summary["R.Condition"]=ptmcvs["R.Condition"]
        ptmcvs_summary["Protein Mean CVs"]=proteinptmcv_mean
        ptmcvs_summary["Protein Median CVs"]=proteinptmcv_median
        ptmcvs_summary["Protein Mean CVs 95%"]=proteinptmcv95_mean
        ptmcvs_summary["Protein Median CVs 95%"]=proteinptmcv95_median

        ptmcvs_summary["Precursor Mean CVs"]=precursorptmcv_mean
        ptmcvs_summary["Precursor Median CVs"]=precursorptmcv_median
        ptmcvs_summary["Precursor Mean CVs 95%"]=precursorptmcv95_mean
        ptmcvs_summary["Precursor Median CVs 95%"]=precursorptmcv95_median

        ptmcvs_summary["Peptide Mean CVs"]=peptideptmcv_mean
        ptmcvs_summary["Peptide Median CVs"]=peptideptmcv_median
        ptmcvs_summary["Peptide Mean CVs 95%"]=peptideptmcv95_mean
        ptmcvs_summary["Peptide Median CVs 95%"]=peptideptmcv95_median

        cvplotinput=input.ptm_proteins_precursors()
        cutoff95=input.ptm_removetop5percent()
        if cvplotinput=="Protein":
            if cutoff95==True:
                return ptmcvs_summary[["R.Condition","Protein Mean CVs 95%","Protein Median CVs 95%"]]
            if cutoff95==False:
                return ptmcvs_summary[["R.Condition","Protein Mean CVs","Protein Median CVs"]]
        if cvplotinput=="Precursor":
            if cutoff95==True:
                return ptmcvs_summary[["R.Condition","Precursor Mean CVs 95%","Precursor Median CVs 95%"]]
            if cutoff95==False:
                return ptmcvs_summary[["R.Condition","Precursor Mean CVs","Precursor Median CVs"]]
        if cvplotinput=="Peptide":
            if cutoff95==True:
                return ptmcvs_summary[["R.Condition","Peptide Mean CVs 95%","Peptide Median CVs 95%"]]
            if cutoff95==False:
                return ptmcvs_summary[["R.Condition","Peptide Mean CVs","Peptide Median CVs"]]

    # ====================================== PTMs per Precursor
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
                frequencies=pd.Series(numptms).value_counts().sort_index()
                if numconditions==1:
                    ax.bar(x+(j*width),frequencies,width=width,color=colors,edgecolor="black")
                else:
                    ax.bar(x+(j*width),frequencies,width=width,color=colors[j],edgecolor="black")
                ax.bar_label(ax.containers[j],label_type="edge",rotation=90,padding=5,fontsize=labelfont)

            ax.legend(sampleconditions,loc="upper right",fontsize=legendfont)
            ax.set_ylim(bottom=-ax.get_ylim()[1]+0.9*ax.get_ylim()[1],top=ax.get_ylim()[1]+y_padding*ax.get_ylim()[1])
            ax.set_xticks(x+((numconditions-1)/2)*width,x)
            ax.tick_params(axis="both",labelsize=axisfont)
            ax.set_ylabel("Counts",fontsize=axisfont)
            ax.set_xlabel("# of PTMs",fontsize=axisfont)
            ax.set_title("# of PTMs per Precursor",fontsize=titlefont)
            ax.set_axisbelow(True)
            ax.grid(linestyle="--")

    # ====================================== Mass Accuracy
    @render.ui
    def ptm_massaccuracy_bins_ui():
        if input.ptm_massaccuracy_violin_hist()=="histogram":
            return ui.input_slider("ptm_massaccuracy_hist_bins","Number of bins",min=10,max=200,value=100,step=10,ticks=True,width="300px")
    #plot mass accuracy
    @reactive.effect
    def _():
        @render.plot(width=input.ptm_massaccuracy_width(),height=input.ptm_massaccuracy_height())
        def ptm_massaccuracy_plot():
            searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
            ptmresultdf,ptm=ptmcounts()

            massaccuracy_df=pd.DataFrame()
            massaccuracy_df["Cond_Rep"]=searchoutput["Cond_Rep"].drop_duplicates().reset_index(drop=True)
            massaccuracy=[]
            for run in searchoutput["Cond_Rep"].drop_duplicates().tolist():
                massaccuracylist=searchoutput[(searchoutput["Cond_Rep"]==run)&(searchoutput["EG.ModifiedPeptide"].str.contains(ptm))]["FG.CalibratedMassAccuracy (PPM)"].dropna().tolist()
                massaccuracy.append(massaccuracylist)

            massaccuracy_df["Mass Accuracy"]=massaccuracy

            violincolors=replicatecolors()
            titlefont=input.titlefont()
            axisfont=input.axisfont()
            labelfont=input.labelfont()

            if input.ptm_massaccuracy_violin_hist()=="violin":
                fig,ax=plt.subplots()
                medianlineprops=dict(linestyle="--",color="black")
                flierprops=dict(markersize=3)
                x=np.arange(len(massaccuracy_df["Cond_Rep"].tolist()))
                plot=ax.violinplot(massaccuracy_df["Mass Accuracy"],showextrema=False)
                ax.boxplot(massaccuracy_df["Mass Accuracy"],medianprops=medianlineprops,flierprops=flierprops)
                ax.set_ylabel("Mass Accuracy (ppm)",fontsize=axisfont)
                ax.set_xlabel("Run",fontsize=axisfont)
                ax.set_title(ptm+"Precursor Mass Accuracy",fontsize=titlefont)
                ax.set_xticks(x+1,labels=massaccuracy_df["Cond_Rep"].tolist(),rotation=input.xaxis_label_rotation())
                ax.grid(linestyle="--")
                ax.set_axisbelow(True)

                if numconditions==1:
                    for z in plot["bodies"]:
                        z.set_facecolor(violincolors)
                        z.set_edgecolor("black")
                        z.set_alpha(0.7)
                else:
                    for z,color in zip(plot["bodies"],violincolors):
                        z.set_facecolor(color)
                        z.set_edgecolor("black")
                        z.set_alpha(0.7)

            if input.ptm_massaccuracy_violin_hist()=="histogram":
                if numsamples==1:
                    fig,ax=plt.subplots()
                    ax.hist(massaccuracy_df["Mass Accuracy"],bins=input.ptm_massaccuracy_hist_bins(),color=violincolors)
                    ax.set_xlabel("Mass Accuracy (ppm)",fontsize=axisfont)
                    ax.set_ylabel("Frequency",fontsize=axisfont)
                    ax.set_title(ptm+"Precursor Mass Accuracy",fontsize=titlefont)
                    ax.grid(linestyle="--")
                    ax.set_axisbelow(True)
                else:
                    fig,ax=plt.subplots(ncols=len(massaccuracy_df["Cond_Rep"]))
                    for i,run in enumerate(massaccuracy_df["Cond_Rep"]):
                        if numconditions==1:
                            ax[i].hist(massaccuracy_df["Mass Accuracy"][i],bins=input.ptm_massaccuracy_hist_bins(),color=violincolors)
                        else:
                            ax[i].hist(massaccuracy_df["Mass Accuracy"][i],bins=input.ptm_massaccuracy_hist_bins(),color=violincolors[i])
                        ax[i].set_xlabel("Mass Accuracy (ppm)",fontsize=axisfont)
                        ax[i].set_title(run,fontsize=titlefont)
                        ax[i].grid(linestyle="--")
                        ax[i].set_axisbelow(True)
                    ax[0].set_ylabel("Frequency",fontsize=axisfont)
                    plt.suptitle(ptm+"Precursor Mass Accuracy",fontsize=titlefont)

#endregion

# ============================================================================= Heatmaps
#region
    # ====================================== RT, m/z, IM Heatmaps
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
    @reactive.effect
    def _():
        @render.plot(width=input.heatmap_width(),height=input.heatmap_height())
        def replicate_heatmap():
            searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()

            titlefont=input.titlefont()
            axisfont=input.axisfont()
            labelfont=input.labelfont()

            numbins=input.heatmap_numbins()

            conditioninput=input.cond_rep_heatmap()
            if input.conditiontype()=="replicate":
                his2dsample=searchoutput[searchoutput["Cond_Rep"]==conditioninput][["Cond_Rep","EG.IonMobility","EG.ApexRT","FG.PrecMz","FG.MS2Quantity"]].sort_values(by="EG.ApexRT").reset_index(drop=True)
            elif input.conditiontype()=="condition":
                his2dsample=searchoutput[searchoutput["R.Condition"]==conditioninput][["R.Condition","EG.IonMobility","EG.ApexRT","FG.PrecMz","FG.MS2Quantity"]].sort_values(by="EG.ApexRT").reset_index(drop=True)

            samplename=conditioninput
            if input.heatmap_cmap()=="default":
                cmap=matplotlib.colors.LinearSegmentedColormap.from_list("",["white","blue","red"])
            else:
                cmap=input.heatmap_cmap()

            fig,ax=plt.subplots(nrows=2,ncols=2)

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

            if len(his2dsample["FG.MS2Quantity"].drop_duplicates())==1:
                ax[1,0].remove()
            else:
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

    # ====================================== Charge/PTM Precursor Heatmap
    #download windows template
    @render.download(filename="dia_windows_template.csv")
    def diawindows_template():
        template_df=pd.DataFrame(columns=[
            "#MS Type",
            "Cycle Id",
            "Start IM [1/K0]",
            "End IM [1/K0]",
            "Start Mass [m/z]",
            "End Mass [m/z]",
            "CE [eV]"
            ])
        with io.BytesIO() as buf:
            template_df.to_csv(buf,index=False)
            yield buf.getvalue()
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
    #bremen DIA windows
    def bremendiawindow():
        bremendia=pd.DataFrame({
            "#MS Type":['PASEF','PASEF','PASEF','PASEF','PASEF','PASEF','PASEF','PASEF','PASEF','PASEF','PASEF','PASEF','PASEF','PASEF','PASEF','PASEF','PASEF','PASEF','PASEF','PASEF','PASEF','PASEF','PASEF','PASEF'],
            "Cycle Id":[1,1,1,2,2,2,3,3,3,4,4,4,5,5,5,6,6,6,7,7,7,8,8,8],
            "Start IM [1/K0]":[0.64,0.83,1.01,0.64,0.85,1.04,0.64,0.87,1.06,0.64,0.9,1.09,0.64,0.92,1.11,0.64,0.94,1.13,0.64,0.97,1.16,0.64,0.99,1.18],
            "End IM [1/K0]":[0.83,1.01,1.37,0.85,1.04,1.37,0.87,1.06,1.37,0.9,1.09,1.37,0.92,1.11,1.37,0.94,1.13,1.37,0.97,1.16,1.37,0.99,1.18,1.37],
            "Start Mass [m/z]":[400,600,800,425,625,825,450,650,850,475,675,875,500,700,900,525,725,925,550,750,950,575,775,975],
            "End Mass [m/z]":[425,625,825,450,650,850,475,675,875,500,700,900,525,725,925,550,750,950,575,775,975,600,800,1000],
            "CE [eV]":['-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-'],
            "W":[25,25,25,25,25,25,25,25,25,25,25,25,25,25,25,25,25,25,25,25,25,25,25,25],
            "H":[0.19,0.18,0.36,0.21,0.19,0.33,0.23,0.19,0.31,0.26,0.19,0.28,0.28,0.19,0.26,0.3,0.19,0.24,0.33,0.19,0.21,0.35,0.19,0.19],
            "xy":[(400,0.64),(600,0.83),(800,1.01),(425,0.64),(625,0.85),(825,1.04),(450,0.64),(650,0.87),(850,1.06),(475,0.64),(675,0.9),(875,1.09),(500,0.64),(700,0.92),(900,1.11),(525,0.64),(725,0.94),(925,1.13),(550,0.64),(750,0.97),(950,1.16),(575,0.64),(775,0.99),(975,1.18)],
        })
        return bremendia

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
    @reactive.effect
    def _():
        @render.plot(width=input.chargeptmheatmap_width(),height=input.chargeptmheatmap_height())
        def chargeptmheatmap():
            searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()

            charge=input.chargestates_chargeptmheatmap_list()
            ptm=input.ptm_chargeptmheatmap_list()

            numbins_x=input.chargeptm_numbins_x()
            numbins_y=input.chargeptm_numbins_y()
            numbins=[numbins_x,numbins_y]

            if input.chargeptmheatmap_cmap()=="default":
                cmap=matplotlib.colors.LinearSegmentedColormap.from_list("",["white","blue","red"])
            else:
                cmap=input.chargeptmheatmap_cmap()

            titlefont=input.titlefont()
            axisfont=input.axisfont()

            fig,ax=plt.subplots()

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
            #ax.set_xlim(100,1700)
            
            fig.set_tight_layout(True)
            
            if input.windows_choice()!="None":
                if input.windows_choice()=="lubeck":
                    diawindows=lubeckdiawindow()
                elif input.windows_choice()=="phospho":
                    diawindows=phosphodiawindow()
                elif input.windows_choice()=="bremen":
                    diawindows=bremendiawindow()
                elif input.windows_choice()=="imported":
                    diawindows=diawindows_import()

                for i in range(len(diawindows)):
                    rect=matplotlib.patches.Rectangle(xy=diawindows["xy"][i],width=diawindows["W"][i],height=diawindows["H"][i],facecolor="red",alpha=0.1,edgecolor="grey")
                    ax.add_patch(rect) 

    # ====================================== Charge/PTM Precursor Scatter
    #render ui call for dropdown calling Cond_Rep column
    @render.ui
    def chargeptmscatter_cond_rep():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
        opts=resultdf["Cond_Rep"].tolist()
        return ui.input_selectize("chargeptmscatter_cond_rep_pick","Pick run:",choices=opts)
    #render ui call for dropdown calling PTMs that were detected
    @render.ui
    def ptm_chargeptmscatter_ui():
        listofptms=find_ptms()
        ptmshortened=[]
        for i in range(len(listofptms)):
            ptmshortened.append(re.sub(r'\(.*?\)',"",listofptms[i]))
        ptmdict={ptmshortened[i]: listofptms[i] for i in range(len(listofptms))}
        nonedict={"None":"None"}
        ptmdict=(nonedict | ptmdict)
        return ui.input_selectize("ptm_chargeptmscatter_list","Pick PTM to plot data for (use None for all precursors):",choices=ptmdict,selected="None")
    #render ui call for dropdown calling charge states that were detected
    @render.ui
    def chargestates_chargeptmscatter_ui():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
        mincharge=min(searchoutput["FG.Charge"])
        maxcharge=max(searchoutput["FG.Charge"])
        opts=[item for item in range(mincharge,maxcharge+1)]
        if input.ptm_chargeptmscatter_list()!="None":
            opts.insert(0,0)
        return ui.input_selectize("chargestates_chargeptmscatter_list","Pick charge to plot data for:",choices=opts)
    #scatterplot of picked PTM or charge against the rest of the detected precursors (better for DDA to show charge groups in the heatmap)
    @reactive.effect
    def _():
        @render.plot(width=input.chargeptmscatter_width(),height=input.chargeptmscatter_height())
        def chargeptmscatter():
            searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
            
            axisfont=input.axisfont()
            legendfont=input.legendfont()

            ptm=input.ptm_chargeptmscatter_list()
            charge=int(input.chargestates_chargeptmscatter_list())
            cond_rep_pick=input.chargeptmscatter_cond_rep_pick()

            # if input.charge_or_ptm()=="charge":
            #     charge=int(input.charge_ptm_list())
            #     precursor_pick=searchoutput[((searchoutput["FG.Charge"]==charge)==True)&(searchoutput["Cond_Rep"]==cond_rep_pick)]
            #     precursor_other=searchoutput[((searchoutput["FG.Charge"]==charge)==False)&(searchoutput["Cond_Rep"]==cond_rep_pick)]
            #     titlemod=str(charge)+"+ Precursors"
            # if input.charge_or_ptm()=="ptm":
            #     ptm=input.charge_ptm_list()
            #     precursor_pick=searchoutput[(searchoutput["EG.ModifiedPeptide"].str.contains(ptm)==True)&(searchoutput["Cond_Rep"]==cond_rep_pick)]
            #     precursor_other=searchoutput[(searchoutput["EG.ModifiedPeptide"].str.contains(ptm)==False)&(searchoutput["Cond_Rep"]==cond_rep_pick)]
            #     titlemod=ptm.split("(")[0]+"Precursors"

            if ptm=="None":
                #all ptms, specific charge
                precursor_pick=searchoutput[((searchoutput["FG.Charge"]==charge)==True)&(searchoutput["Cond_Rep"]==cond_rep_pick)]
                precursor_other=searchoutput[((searchoutput["FG.Charge"]==charge)==False)&(searchoutput["Cond_Rep"]==cond_rep_pick)]
                titlemod=str(charge)+"+ Precursors"
            if ptm!="None":
                #specific ptm, all charges
                # if charge==0:
                #     precursor_pick=searchoutput[(searchoutput["EG.ModifiedPeptide"].str.contains(ptm)==True)&(searchoutput["Cond_Rep"]==cond_rep_pick)]
                #     precursor_other=searchoutput[(searchoutput["EG.ModifiedPeptide"].str.contains(ptm)==False)&(searchoutput["Cond_Rep"]==cond_rep_pick)]
                #     titlemod=ptm.split("(")[0]+"Precursors"
                # #specific ptm, specific charge
                #elif charge!=0:
                precursor_pick=searchoutput[(searchoutput["EG.ModifiedPeptide"].str.contains(ptm)==True)&((searchoutput["FG.Charge"]==charge)==True)&(searchoutput["Cond_Rep"]==cond_rep_pick)]
                #for some reason there's a bug with only +2 charge where the precursor_other wouldn't display correctly
                precursor_other=searchoutput[(searchoutput["EG.ModifiedPeptide"].str.contains(ptm)==False)&(searchoutput["Cond_Rep"]==cond_rep_pick)]#&((searchoutput["FG.Charge"]==charge)==False)
                titlemod=ptm.split("(")[0]+str(charge)+"+ Precursors"

            fig,ax=plt.subplots()
            ax.scatter(x=precursor_other["FG.PrecMz"],y=precursor_other["EG.IonMobility"],s=2,label="All Other Precursors")
            ax.scatter(x=precursor_pick["FG.PrecMz"],y=precursor_pick["EG.IonMobility"],s=2,label=titlemod)
            ax.set_xlabel("m/z",fontsize=axisfont)
            ax.set_ylabel("Ion Mobility ($1/K_{0}$)",fontsize=axisfont)
            ax.legend(loc="upper left",fontsize=legendfont,markerscale=5)
            ax.set_axisbelow(True)
            ax.grid(linestyle="--")
    #show table of # of precursors selected in charge-ptm scatterplot
    @render.table
    def chargeptmscatter_table():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
        ptm=input.ptm_chargeptmscatter_list()
        cond_rep_pick=input.chargeptmscatter_cond_rep_pick()

        if ptm=="None":
            #all ptms
            precursor_pick=searchoutput[(searchoutput["Cond_Rep"]==cond_rep_pick)]
        if ptm!="None":
            #specific ptm
            precursor_pick=searchoutput[(searchoutput["EG.ModifiedPeptide"].str.contains(ptm)==True)&(searchoutput["Cond_Rep"]==cond_rep_pick)]

        sortedchargelist=sorted(precursor_pick["FG.Charge"].drop_duplicates().tolist())
        charge_populationlist=[]
        for charge in sortedchargelist:
            charge_populationlist.append(len(precursor_pick[precursor_pick["FG.Charge"]==charge]))

        sortedchargelist.insert(0,"Sum")
        charge_populationlist.insert(0,sum(charge_populationlist))

        df=pd.DataFrame({"Charge":sortedchargelist,"# Precursors":charge_populationlist})
        
        return df

    # ====================================== IDs vs RT
    @render.ui
    def binslider_ui():
        return ui.input_slider("binslider","Number of RT bins:",min=100,max=1000,step=50,value=500,ticks=True)
    #render ui for checkboxes to plot specific runs
    @render.ui
    def ids_vs_rt_checkbox():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
        keys=resultdf["Cond_Rep"].tolist()
        opts=dict()
        for x in keys:
            opts[x]=x
        return ui.input_checkbox_group("ids_vs_rt_checkbox_pick","Pick runs to plot data for:",choices=opts)
    #plot # of IDs vs RT for each run
    @reactive.effect
    def _():
        @render.plot(width=input.idsvsrt_width(),height=input.idsvsrt_height())
        def ids_vs_rt():
            searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
            
            rtmax=float(math.ceil(max(searchoutput["EG.ApexRT"]))) #needs to be a float
            numbins=input.binslider()
            runlist=input.ids_vs_rt_checkbox_pick()

            bintime=rtmax/numbins*60

            titlefont=input.titlefont()
            axisfont=input.axisfont()
            legendfont=input.legendfont()

            fig,ax=plt.subplots()

            for run in runlist:
                rt_run=searchoutput[searchoutput["Cond_Rep"]==run]["EG.ApexRT"]
                if rt_run.empty:
                    continue
                hist=np.histogram(rt_run,bins=numbins,range=(0.0,rtmax))
                ax.plot(np.delete(hist[1],0),hist[0],linewidth=0.5,label=run)

            ax.set_ylabel("# of IDs",fontsize=axisfont)
            ax.set_xlabel("RT (min)",fontsize=axisfont)
            ax.tick_params(axis="both",labelsize=axisfont)
            ax.text(0,(ax.get_ylim()[1]-(0.1*ax.get_ylim()[1])),"~"+str(round(bintime,2))+" s per bin",fontsize=axisfont)
            legend=ax.legend(loc='center left', bbox_to_anchor=(1, 0.5),prop={'size':legendfont})
            for i in legend.legend_handles:
                i.set_linewidth(5)
            ax.set_axisbelow(True)
            ax.grid(linestyle="--")
            ax.set_title("# of Precursor IDs vs RT",fontsize=titlefont)

    # ====================================== Venn Diagram
    @render.ui
    def venn_run1_ui():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
        if input.venn_conditionorrun()=="condition":
            opts=resultdf["R.Condition"].drop_duplicates().tolist()
            return ui.input_selectize("venn_run1_list","Pick first condition to compare",choices=opts)
        if input.venn_conditionorrun()=="individual":
            opts=resultdf["Cond_Rep"].tolist()
            return ui.input_selectize("venn_run1_list","Pick first run to compare",choices=opts)   
    @render.ui
    def venn_run2_ui():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
        if input.venn_conditionorrun()=="condition":
            opts=resultdf["R.Condition"].drop_duplicates().tolist()
            return ui.input_selectize("venn_run2_list","Pick second condition to compare",choices=opts)
        if input.venn_conditionorrun()=="individual":
            opts=resultdf["Cond_Rep"].tolist()
            return ui.input_selectize("venn_run2_list","Pick second run to compare",choices=opts)   
    @render.ui
    def venn_run3_ui():
        if input.venn_numcircles()=="3":
            searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
            if input.venn_conditionorrun()=="condition":
                opts=resultdf["R.Condition"].drop_duplicates().tolist()
                return ui.input_selectize("venn_run3_list","Pick third condition to compare",choices=opts)
            if input.venn_conditionorrun()=="individual":
                opts=resultdf["Cond_Rep"].tolist()
                return ui.input_selectize("venn_run3_list","Pick third run to compare",choices=opts)
    @render.ui
    def venn_specific_length_ui():
        if input.venn_plotproperty()=="peptides" or input.venn_plotproperty()=="precursors" or input.venn_plotproperty()=="peptides_stripped":
            return ui.input_switch("venn_specific_length","Compare specific peptide length?",value=False,width="300px")
    @render.ui
    def venn_peplength_ui():
        if input.venn_specific_length()==True:
            return ui.input_slider("venn_peplength_pick","Pick specific peptide length to compare:",min=3,max=30,value=9,step=1,ticks=True)
    @render.ui
    def peptidecore_ui():
        if input.venn_plotproperty()=="peptides_stripped":
            return ui.input_switch("peptidecore","Only consider peptide core (cut first and last 2 residues)",value=False)
    @render.ui
    def venn_ptm_ui():
        if input.venn_plotproperty()=="peptides" or input.venn_plotproperty()=="precursors" or input.venn_plotproperty()=="peptides_stripped":
            return ui.input_switch("venn_ptm","Compare only for specific PTM?",value=False)
    @render.ui
    def venn_ptmlist_ui():
        if input.venn_plotproperty()=="peptides" or input.venn_plotproperty()=="precursors" or input.venn_plotproperty()=="peptides_stripped":
            if input.venn_ptm()==True:
                listofptms=find_ptms()
                ptmshortened=[]
                for i in range(len(listofptms)):
                    ptmshortened.append(re.sub(r'\(.*?\)',"",listofptms[i]))
                ptmdict={ptmshortened[i]: listofptms[i] for i in range(len(listofptms))}
                return ui.input_selectize("venn_foundptms","Pick PTM to plot data for",choices=ptmdict,selected=listofptms[0])  
    #plot Venn Diagram
    @reactive.effect
    def _():
        @render.plot(width=input.venn_width(),height=input.venn_height())
        def venn_plot():
            searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
            if input.venn_conditionorrun()=="condition":
                A=searchoutput[searchoutput["R.Condition"]==input.venn_run1_list()][["PG.ProteinGroups","EG.ModifiedPeptide","FG.Charge","PEP.StrippedSequence"]].drop_duplicates().reset_index(drop=True)
                B=searchoutput[searchoutput["R.Condition"]==input.venn_run2_list()][["PG.ProteinGroups","EG.ModifiedPeptide","FG.Charge","PEP.StrippedSequence"]].drop_duplicates().reset_index(drop=True)
                if input.venn_numcircles()=="3":
                    C=searchoutput[searchoutput["R.Condition"]==input.venn_run3_list()][["PG.ProteinGroups","EG.ModifiedPeptide","FG.Charge","PEP.StrippedSequence"]].drop_duplicates().reset_index(drop=True)
            if input.venn_conditionorrun()=="individual":
                A=searchoutput[searchoutput["Cond_Rep"]==input.venn_run1_list()][["PG.ProteinGroups","EG.ModifiedPeptide","FG.Charge","PEP.StrippedSequence"]].drop_duplicates().reset_index(drop=True)
                B=searchoutput[searchoutput["Cond_Rep"]==input.venn_run2_list()][["PG.ProteinGroups","EG.ModifiedPeptide","FG.Charge","PEP.StrippedSequence"]].drop_duplicates().reset_index(drop=True)
                if input.venn_numcircles()=="3":
                    C=searchoutput[searchoutput["Cond_Rep"]==input.venn_run3_list()][["PG.ProteinGroups","EG.ModifiedPeptide","FG.Charge","PEP.StrippedSequence"]].drop_duplicates().reset_index(drop=True)
            
            #add extra columns to df for peptide+charge and peptide lengths
            A["pep_charge"]=A["EG.ModifiedPeptide"]+A["FG.Charge"].astype(str)
            B["pep_charge"]=B["EG.ModifiedPeptide"]+B["FG.Charge"].astype(str)
            if input.venn_numcircles()=="3":
                C["pep_charge"]=C["EG.ModifiedPeptide"]+C["FG.Charge"].astype(str)
                C_peplength=[]
                for pep in C["PEP.StrippedSequence"]:
                    C_peplength.append(len(pep))
                C["Peptide Length"]=C_peplength
            A_peplength=[]
            for pep in A["PEP.StrippedSequence"]:
                A_peplength.append(len(pep))
            A["Peptide Length"]=A_peplength
            B_peplength=[]
            for pep in B["PEP.StrippedSequence"]:
                B_peplength.append(len(pep))
            B["Peptide Length"]=B_peplength
            
            titlemodlist=[]

            if input.venn_plotproperty()=="proteingroups":
                a=set(A["PG.ProteinGroups"])
                b=set(B["PG.ProteinGroups"])
                if input.venn_numcircles()=="3":
                    c=set(C["PG.ProteinGroups"])
                titlemod="Protein Groups"
            if input.venn_plotproperty()=="peptides":
                if input.venn_ptm()==True:
                    ptm=input.venn_foundptms()
                    A=A[A["EG.ModifiedPeptide"].str.contains(ptm)]
                    B=B[B["EG.ModifiedPeptide"].str.contains(ptm)]
                    if input.venn_numcircles()=="3":
                        C=C[C["EG.ModifiedPeptide"].str.contains(ptm)]
                    titlemodlist.append(ptm.strip())
                if input.venn_specific_length()==True:
                    A=A[A["Peptide Length"]==int(input.venn_peplength_pick())]
                    B=B[B["Peptide Length"]==int(input.venn_peplength_pick())]
                    if input.venn_numcircles()=="3":
                        C=C[C["Peptide Length"]==int(input.venn_peplength_pick())]
                    titlemodlist.append(str(input.venn_peplength_pick())+"mers")
                if input.venn_ptm()==False and input.venn_specific_length()==False:
                    A=A
                    B=B
                    if input.venn_numcircles()=="3":
                        C=C
                a=set(A["EG.ModifiedPeptide"])
                b=set(B["EG.ModifiedPeptide"])
                if input.venn_numcircles()=="3":
                    c=set(C["EG.ModifiedPeptide"])
                titlemod="Peptides"
            if input.venn_plotproperty()=="precursors":
                if input.venn_ptm()==True:
                    ptm=input.venn_foundptms()
                    A=A[A["EG.ModifiedPeptide"].str.contains(ptm)]
                    B=B[B["EG.ModifiedPeptide"].str.contains(ptm)]
                    if input.venn_numcircles()=="3":
                        C=C[C["EG.ModifiedPeptide"].str.contains(ptm)]
                    titlemodlist.append(ptm.strip())
                if input.venn_specific_length()==True:
                    A=A[A["Peptide Length"]==int(input.venn_peplength_pick())]
                    B=B[B["Peptide Length"]==int(input.venn_peplength_pick())]
                    if input.venn_numcircles()=="3":
                        C=C[C["Peptide Length"]==int(input.venn_peplength_pick())]
                    titlemodlist.append(str(input.venn_peplength_pick())+"mers")
                else:
                    A=A
                    B=B
                    if input.venn_numcircles()=="3":
                        C=C
                a=set(A["pep_charge"])
                b=set(B["pep_charge"])
                if input.venn_numcircles()=="3":
                    c=set(C["pep_charge"])
                titlemod="Precursors"
            if input.venn_plotproperty()=="peptides_stripped":
                if input.venn_ptm()==True:
                    ptm=input.venn_foundptms()
                    A=A[A["EG.ModifiedPeptide"].str.contains(ptm)]
                    B=B[B["EG.ModifiedPeptide"].str.contains(ptm)]
                    if input.venn_numcircles()=="3":
                        C=C[C["EG.ModifiedPeptide"].str.contains(ptm)]
                    titlemodlist.append(ptm.strip())
                if input.venn_specific_length()==True:
                    A=A[A["Peptide Length"]==int(input.venn_peplength_pick())]
                    B=B[B["Peptide Length"]==int(input.venn_peplength_pick())]
                    if input.venn_numcircles()=="3":
                        C=C[C["Peptide Length"]==int(input.venn_peplength_pick())]
                    titlemodlist.append(str(input.venn_peplength_pick())+"mers")
                else:
                    A=A
                    B=B
                    if input.venn_numcircles()=="3":
                        C=C
                if input.peptidecore()==True:
                    A_coreAA=[]
                    B_coreAA=[]
                    for pep in A["PEP.StrippedSequence"].tolist():
                        A_coreAA.append(pep[2:-2])
                    for pep in B["PEP.StrippedSequence"].tolist():
                        B_coreAA.append(pep[2:-2])
                    a=set(A_coreAA)
                    b=set(B_coreAA)
                    if input.venn_numcircles()=="3":
                        C_coreAA=[]
                        for pep in C["PEP.StrippedSequence"].tolist():
                            C_coreAA.append(pep[2:-2])
                        c=set(C_coreAA)
                    titlemod="Stripped Peptides (no terminal AAs)"
                else:
                    a=set(A["PEP.StrippedSequence"])
                    b=set(B["PEP.StrippedSequence"])
                    if input.venn_numcircles()=="3":
                        c=set(C["PEP.StrippedSequence"])
                    titlemod="Stripped Peptides"
            if titlemodlist==[]:
                titlemodlist=""
            else:
                titlemodlist=" ("+", ".join(titlemodlist)+")"
            fig,ax=plt.subplots()
            if input.venn_numcircles()=="2":
                Ab=len(a-b)
                aB=len(b-a)
                AB=len(a&b)
                venn2(subsets=(Ab,aB,AB),set_labels=(input.venn_run1_list(),input.venn_run2_list()),set_colors=("tab:blue","tab:orange"),ax=ax)
                venn2_circles(subsets=(Ab,aB,AB),linestyle="dashed",linewidth=0.5)
                plt.title("Venn Diagram for "+titlemod+titlemodlist)
            if input.venn_numcircles()=="3":
                Abc=len(a-b-c)
                aBc=len(b-a-c)
                ABc=len((a&b)-c)
                abC=len(c-a-b)
                AbC=len((a&c)-b)
                aBC=len((b&c)-a)
                ABC=len(a&b&c)
                venn3(subsets=(Abc,aBc,ABc,abC,AbC,aBC,ABC),set_labels=(input.venn_run1_list(),input.venn_run2_list(),input.venn_run3_list()),set_colors=("tab:blue","tab:orange","tab:green"),ax=ax)
                venn3_circles(subsets=(Abc,aBc,ABc,abC,AbC,aBC,ABC),linestyle="dashed",linewidth=0.5)
                plt.title("Venn Diagram for "+titlemod+titlemodlist)
    #download table of Venn Diagram intersections
    @reactive.effect
    def _():
        if input.venn_numcircles()=="2":
            filename=lambda: f"VennList_{input.venn_run1_list()}_vs_{input.venn_run2_list()}_{input.venn_plotproperty()}.csv"
        if input.venn_numcircles()=="3":
            filename=lambda: f"VennList_A-{input.venn_run1_list()}_vs_B-{input.venn_run2_list()}_vs_C-{input.venn_run3_list()}_{input.venn_plotproperty()}.csv"
        @render.download(filename=filename)
        def venn_download():
            searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
            if input.venn_conditionorrun()=="condition":
                A=searchoutput[searchoutput["R.Condition"]==input.venn_run1_list()][["PG.ProteinGroups","EG.ModifiedPeptide","FG.Charge","PEP.StrippedSequence"]].drop_duplicates().reset_index(drop=True)
                B=searchoutput[searchoutput["R.Condition"]==input.venn_run2_list()][["PG.ProteinGroups","EG.ModifiedPeptide","FG.Charge","PEP.StrippedSequence"]].drop_duplicates().reset_index(drop=True)
                if input.venn_numcircles()=="3":
                    C=searchoutput[searchoutput["R.Condition"]==input.venn_run3_list()][["PG.ProteinGroups","EG.ModifiedPeptide","FG.Charge","PEP.StrippedSequence"]].drop_duplicates().reset_index(drop=True)
            if input.venn_conditionorrun()=="individual":
                A=searchoutput[searchoutput["Cond_Rep"]==input.venn_run1_list()][["PG.ProteinGroups","EG.ModifiedPeptide","FG.Charge","PEP.StrippedSequence"]].drop_duplicates().reset_index(drop=True)
                B=searchoutput[searchoutput["Cond_Rep"]==input.venn_run2_list()][["PG.ProteinGroups","EG.ModifiedPeptide","FG.Charge","PEP.StrippedSequence"]].drop_duplicates().reset_index(drop=True)
                if input.venn_numcircles()=="3":
                    C=searchoutput[searchoutput["Cond_Rep"]==input.venn_run3_list()][["PG.ProteinGroups","EG.ModifiedPeptide","FG.Charge","PEP.StrippedSequence"]].drop_duplicates().reset_index(drop=True)
            
            #add extra columns to df for peptide+charge and peptide lengths
            A["pep_charge"]=A["EG.ModifiedPeptide"]+A["FG.Charge"].astype(str)
            B["pep_charge"]=B["EG.ModifiedPeptide"]+B["FG.Charge"].astype(str)
            if input.venn_numcircles()=="3":
                C["pep_charge"]=C["EG.ModifiedPeptide"]+C["FG.Charge"].astype(str)
                C_peplength=[]
                for pep in C["PEP.StrippedSequence"]:
                    C_peplength.append(len(pep))
                C["Peptide Length"]=C_peplength
            A_peplength=[]
            for pep in A["PEP.StrippedSequence"]:
                A_peplength.append(len(pep))
            A["Peptide Length"]=A_peplength
            B_peplength=[]
            for pep in B["PEP.StrippedSequence"]:
                B_peplength.append(len(pep))
            B["Peptide Length"]=B_peplength

            if input.venn_plotproperty()=="proteingroups":
                a=set(A["PG.ProteinGroups"])
                b=set(B["PG.ProteinGroups"])
                if input.venn_numcircles()=="3":
                    c=set(C["PG.ProteinGroups"])
            if input.venn_plotproperty()=="peptides":
                if input.venn_ptm()==True:
                    ptm=input.venn_foundptms()
                    A=A[A["EG.ModifiedPeptide"].str.contains(ptm)]
                    B=B[B["EG.ModifiedPeptide"].str.contains(ptm)]
                    if input.venn_numcircles()=="3":
                        C=C[C["EG.ModifiedPeptide"].str.contains(ptm)]
                if input.venn_specific_length()==True:
                    A=A[A["Peptide Length"]==int(input.venn_peplength_pick())]
                    B=B[B["Peptide Length"]==int(input.venn_peplength_pick())]
                    if input.venn_numcircles()=="3":
                        C=C[C["Peptide Length"]==int(input.venn_peplength_pick())]
                if input.venn_ptm()==False and input.venn_specific_length()==False:
                    A=A
                    B=B
                    if input.venn_numcircles()=="3":
                        C=C
                a=set(A["EG.ModifiedPeptide"])
                b=set(B["EG.ModifiedPeptide"])
                if input.venn_numcircles()=="3":
                    c=set(C["EG.ModifiedPeptide"])
            if input.venn_plotproperty()=="precursors":
                if input.venn_ptm()==True:
                    ptm=input.venn_foundptms()
                    A=A[A["EG.ModifiedPeptide"].str.contains(ptm)]
                    B=B[B["EG.ModifiedPeptide"].str.contains(ptm)]
                    if input.venn_numcircles()=="3":
                        C=C[C["EG.ModifiedPeptide"].str.contains(ptm)]
                if input.venn_specific_length()==True:
                    A=A[A["Peptide Length"]==int(input.venn_peplength_pick())]
                    B=B[B["Peptide Length"]==int(input.venn_peplength_pick())]
                    if input.venn_numcircles()=="3":
                        C=C[C["Peptide Length"]==int(input.venn_peplength_pick())]
                else:
                    A=A
                    B=B
                    if input.venn_numcircles()=="3":
                        C=C
                a=set(A["pep_charge"])
                b=set(B["pep_charge"])
                if input.venn_numcircles()=="3":
                    c=set(C["pep_charge"])
            if input.venn_plotproperty()=="peptides_stripped":
                if input.venn_ptm()==True:
                    ptm=input.venn_foundptms()
                    A=A[A["EG.ModifiedPeptide"].str.contains(ptm)]
                    B=B[B["EG.ModifiedPeptide"].str.contains(ptm)]
                    if input.venn_numcircles()=="3":
                        C=C[C["EG.ModifiedPeptide"].str.contains(ptm)]
                if input.venn_specific_length()==True:
                    A=A[A["Peptide Length"]==int(input.venn_peplength_pick())]
                    B=B[B["Peptide Length"]==int(input.venn_peplength_pick())]
                    if input.venn_numcircles()=="3":
                        C=C[C["Peptide Length"]==int(input.venn_peplength_pick())]
                else:
                    A=A
                    B=B
                    if input.venn_numcircles()=="3":
                        C=C
                if input.peptidecore()==True:
                    A_coreAA=[]
                    B_coreAA=[]
                    for pep in A["PEP.StrippedSequence"].tolist():
                        A_coreAA.append(pep[2:-2])
                    for pep in B["PEP.StrippedSequence"].tolist():
                        B_coreAA.append(pep[2:-2])
                    a=set(A_coreAA)
                    b=set(B_coreAA)
                    if input.venn_numcircles()=="3":
                        C_coreAA=[]
                        for pep in C["PEP.StrippedSequence"].tolist():
                            C_coreAA.append(pep[2:-2])
                        c=set(C_coreAA)
                else:
                    a=set(A["PEP.StrippedSequence"])
                    b=set(B["PEP.StrippedSequence"])
                    if input.venn_numcircles()=="3":
                        c=set(C["PEP.StrippedSequence"])

            df=pd.DataFrame()
            if input.venn_numcircles()=="2":
                Ab=list(a-b)
                aB=list(b-a)
                AB=list(a&b)
                df=pd.concat([df,pd.Series(Ab,name=input.venn_run1_list())],axis=1)
                df=pd.concat([df,pd.Series(aB,name=input.venn_run2_list())],axis=1)
                df=pd.concat([df,pd.Series(AB,name="Both")],axis=1)
            if input.venn_numcircles()=="3":
                Abc=list(a-b-c)
                aBc=list(b-a-c)
                ABc=list((a&b)-c)
                abC=list(c-a-b)
                AbC=list((a&c)-b)
                aBC=list((b&c)-a)
                ABC=list(a&b&c)
                df=pd.concat([df,pd.Series(Abc,name="A only")],axis=1)
                df=pd.concat([df,pd.Series(aBc,name="B only")],axis=1)
                df=pd.concat([df,pd.Series(ABc,name="A and B, not C")],axis=1)
                df=pd.concat([df,pd.Series(abC,name="C only")],axis=1)
                df=pd.concat([df,pd.Series(AbC,name="A and C, not B")],axis=1)
                df=pd.concat([df,pd.Series(aBC,name="B and C, not A")],axis=1)
                df=pd.concat([df,pd.Series(ABC,name="ABC")],axis=1)
            with io.BytesIO() as buf:
                df.to_csv(buf,index=False)
                yield buf.getvalue()            

    # ====================================== Histogram
    #render ui call for dropdown calling Cond_Rep column
    @render.ui
    def histogram_cond_rep_list():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
        opts=resultdf["Cond_Rep"].tolist()
        return ui.input_checkbox_group("histogram_cond_rep_pick","Pick runs to plot:",choices=opts)
    @reactive.effect
    def _():
        @render.plot(width=input.histogram_width(),height=input.histogram_height())
        def histogram_plot():
            searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
            runlist=input.histogram_cond_rep_pick()
            bins=input.histogram_numbins()
            axisfont=input.axisfont()

            fig,ax=plt.subplots()
            ax.set_ylabel("Counts",fontsize=axisfont)
            for run in runlist:
                df=searchoutput[searchoutput["Cond_Rep"]==run]
                if input.histogram_pick()=="ionmobility":
                    ax.hist(df["EG.IonMobility"],bins=bins,label=run,alpha=0.75)
                    ax.set_xlabel("EG.IonMobility",fontsize=axisfont)
                if input.histogram_pick()=="precursormz":
                    ax.hist(df["FG.PrecMz"],bins=bins,label=run,alpha=0.75)
                    ax.set_xlabel("Precursor m/z",fontsize=axisfont)
                if input.histogram_pick()=="precursorintensity":
                    ax.hist(np.log10(df["FG.MS2Quantity"]),bins=bins,label=run,alpha=0.75)
                    ax.set_xlabel("log10(Precursor Intensity)",fontsize=axisfont)
                if input.histogram_pick()=="proteinintensity":
                    ax.hist(np.log10(df["PG.MS2Quantity"]),bins=bins,label=run,alpha=0.75)
                    ax.set_xlabel("log10(Protein Intensity)",fontsize=axisfont)
            ax.legend()

#endregion

# ============================================================================= Statistics
#region
    # ====================================== Volcano Plot
    #render ui for picking conditions
    @render.ui
    def volcano_condition1():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
        opts=sampleconditions
        return ui.input_selectize("control_condition","Pick control condition",choices=opts)
    @render.ui
    def volcano_condition2():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
        opts=sampleconditions
        return ui.input_selectize("test_condition","Pick test condition",choices=opts,selected=sampleconditions[1])
    #calculation for fold change and p value
    @reactive.calc
    def volcano_calc():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()

        control=input.control_condition()
        test=input.test_condition()

        controldf=searchoutput[searchoutput["R.Condition"]==control][["PG.ProteinGroups","PG.MS2Quantity"]].drop_duplicates().groupby("PG.ProteinGroups")
        testdf=searchoutput[searchoutput["R.Condition"]==test][["PG.ProteinGroups","PG.MS2Quantity"]].drop_duplicates().groupby("PG.ProteinGroups")
        controldf_means=controldf.mean()
        testdf_means=testdf.mean()
        merged=controldf_means.merge(testdf_means,on="PG.ProteinGroups",suffixes=("_control_mean","_test_mean")).reset_index().dropna()

        proteinlist=[]
        controllist=[]
        testlist=[]
        for protein in merged["PG.ProteinGroups"]:
            proteinlist.append(protein)
            controllist.append(list(controldf.get_group(protein)["PG.MS2Quantity"]))
            testlist.append(list(testdf.get_group(protein)["PG.MS2Quantity"]))

        merged["Control"]=controllist
        merged["Test"]=testlist
        merged["log2_FoldChange"]=np.log2(merged["PG.MS2Quantity_test_mean"]/merged["PG.MS2Quantity_control_mean"])

        merged.set_index("PG.ProteinGroups",inplace=True)
        pvalue=[]
        for protein in merged.index:
            pvalue.append(-np.log10(stats.ttest_ind(a=merged.loc[protein]["Control"],b=merged.loc[protein]["Test"])[1]))
        merged["-log10_pvalue"]=pvalue

        pvalue_cutoff=input.volcano_pvalue()
        foldchange_cutoff=input.volcano_foldchange()

        coordlist=[]
        colorlist=[]
        for protein in merged.index:
            if merged.loc[protein]["log2_FoldChange"] >= foldchange_cutoff and np.absolute(merged.loc[protein]["-log10_pvalue"]) >= pvalue_cutoff:
                colorlist.append("r")
                coordlist.append((merged.loc[protein]["log2_FoldChange"],merged.loc[protein]["-log10_pvalue"]))
            elif merged.loc[protein]["log2_FoldChange"] <= -foldchange_cutoff and np.absolute(merged.loc[protein]["-log10_pvalue"]) >= pvalue_cutoff:
                colorlist.append("b")
                coordlist.append((merged.loc[protein]["log2_FoldChange"],merged.loc[protein]["-log10_pvalue"]))
            else:
                colorlist.append("grey")
                coordlist.append("")
                
        merged["color"]=colorlist
        merged["label"]=coordlist

        return merged
    #download a table with values from the volcano plot
    @render.download(filename="volcanoplot_values.csv")
    def volcano_download():
        merged=volcano_calc()
        merged_download=merged[["log2_FoldChange","-log10_pvalue"]].reset_index()
        with io.BytesIO() as buf:
            merged_download.to_csv(buf,index=False)
            yield buf.getvalue()
    #volcano plot
    @reactive.effect
    def _():
        @render.plot(width=input.volcano_width(),height=input.volcano_height())
        def volcanoplot():
            merged=volcano_calc()

            pvalue_cutoff=input.volcano_pvalue()
            foldchange_cutoff=input.volcano_foldchange()

            titlefont=input.titlefont()
            axisfont=input.axisfont()

            fig,ax=plt.subplots()
            ax.scatter(merged["log2_FoldChange"],merged["-log10_pvalue"],s=1,c=merged["color"])
            if input.volcano_h_v_lines()==True:
                ax.axhline(y=pvalue_cutoff,color="black",linestyle="-",linewidth=1)
                ax.axvline(x=foldchange_cutoff,color="black",linestyle="-",linewidth=1)
                ax.axvline(x=-foldchange_cutoff,color="black",linestyle="-",linewidth=1)
            ax.set_xlabel("log2 Fold Change",fontsize=axisfont)
            ax.set_ylabel("-log10 p value",fontsize=axisfont)
            ax.set_title("Control: "+input.control_condition()+", Test: "+input.test_condition(),fontsize=titlefont)
            
            ax.set_axisbelow(True)
            ax.grid(linestyle="--",alpha=0.75)

            if input.volcano_plotrange_switch()==True:
                ax.set_xlim(input.volcano_xplotrange()[0],input.volcano_xplotrange()[1])
                ax.set_ylim(input.volcano_yplotrange()[0],input.volcano_yplotrange()[1])

            if input.show_labels()==True:
                for protein in merged.index:
                    if np.absolute(merged.loc[protein]["log2_FoldChange"]) >= foldchange_cutoff and np.absolute(merged.loc[protein]["-log10_pvalue"]) >= pvalue_cutoff:
                        ax.annotate(protein,merged.loc[protein]["label"],fontsize=input.label_fontsize())
                    else:
                        pass

    # ====================================== Volcano Plot - Feature Plot
    #selectable table for corresponding plot
    @render.data_frame
    def feature_table():
        merged=volcano_calc()
        merged=merged.reset_index().drop(columns=["Control","Test","color","label"])
        return render.DataGrid(merged,width="100%",selection_mode="rows",editable=False)
    #box plot for abundances of selected proteins
    @reactive.effect
    def _():
        @render.plot(width=input.volcano_feature_width(),height=input.volcano_feature_height())
        def feature_plot():
            searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
            if len(feature_table.data_view(selected=True)["PG.ProteinGroups"].tolist())==0:
                fig,ax=plt.subplots()
            else:
                pickedproteins=feature_table.data_view(selected=True)["PG.ProteinGroups"].tolist()

                list_pairs=[searchoutput[searchoutput["PG.ProteinGroups"]==val][["R.Condition","PG.ProteinGroups","PG.MS2Quantity"]].drop_duplicates().reset_index(drop=True) for val in pickedproteins]
                conditions=list_pairs[0]["R.Condition"].drop_duplicates().tolist()

                colorlist=[]
                legend_patches=[]
                for i in range(len(conditions)):
                    colorlist.append(list(mcolors.TABLEAU_COLORS.keys())[i])
                    legend_patches.append(mpatches.Patch(color=list(mcolors.TABLEAU_COLORS.keys())[i],label=conditions[i]))

                lineprops=dict(linestyle="--",color="black")
                fig,ax=plt.subplots()
                positions=list(np.arange(len(conditions)))
                for i in range(len(list_pairs)):
                    plottinglist=[]
                    #make a list of lists of the signals for the given protein in the given condition
                    for condition in conditions:
                        plottinglist.append(list_pairs[i].groupby("R.Condition").get_group(condition)["PG.MS2Quantity"].tolist())
                    bplot=ax.boxplot(plottinglist,positions=positions,widths=0.75,patch_artist=True,medianprops=lineprops)
                    #change box color corresponding to condition
                    for x in range(len(bplot["boxes"])):
                        color=colorlist[x]
                        for item in ["boxes"]:
                            plt.setp(bplot[item][x],color=color)
                    #adjust positions for the next places to plot
                    for y in range(len(positions)):
                        positions[y]+=len(positions)

                xticks=[]
                x=1/(len(conditions))
                for i in range(len(list_pairs)):
                    xticks.append(x)
                    ax.axvline(x=x+1,color="lightgrey",linestyle="--")
                    x+=len(conditions)
                pickedproteins_shortened=[]
                for protein in pickedproteins:
                    if protein.count(";")>=1:
                        pickedproteins_shortened.append(protein.split(";")[0])
                    else:
                        pickedproteins_shortened.append(protein)
                ax.set_xticks(xticks)
                ax.set_xticklabels(pickedproteins_shortened)
                ax.legend(handles=legend_patches)

            axisfont=input.axisfont()

            ax.set_ylabel("Protein Group Intensity",fontsize=axisfont)
            ax.set_xlabel("Protein Group",fontsize=axisfont)
            #ax.grid(axis="y",linestyle="--")

    # ====================================== Volcano Plot - Up/Down Regulation
    #volcano plot up/down regulation protein list
    @reactive.effect
    def _():
        @render.plot(width=input.volcano_regulation_width(),height=input.volcano_regulation_height())
        def volcano_updownregulation_plot():
            merged=volcano_calc()
            plot_up_or_down=input.regulation_upordown()
            top_n=int(input.regulation_topN())
            foldchange_cutoff=input.volcano_foldchange()

            titlefont=input.titlefont()
            axisfont=input.axisfont()

            if plot_up_or_down=="up":
                merged_sort=merged[merged["log2_FoldChange"]>=foldchange_cutoff]["-log10_pvalue"].dropna().sort_values(axis=0,ascending=False).reset_index()
                color="r"
                title="Upregulated Protiens"
            if plot_up_or_down=="down":
                merged_sort=merged[merged["log2_FoldChange"]<=-foldchange_cutoff]["-log10_pvalue"].dropna().sort_values(axis=0,ascending=False).reset_index()
                color="b"
                title="Downregulated Proteins"

            proteinlist=merged_sort["PG.ProteinGroups"].str.split(";").tolist()
            proteinlist_simplified=[]
            for protein in proteinlist:
                proteinlist_simplified.append(protein[0])
            fig,ax=plt.subplots()
            y=np.flip(np.arange(len(merged_sort)))
            ax.barh(y[:top_n],merged_sort["-log10_pvalue"][:top_n],color=color)
            ax.set_yticks(y[:top_n],labels=proteinlist_simplified[:top_n])
            ax.set_xlabel("-log10 pvalue",fontsize=axisfont)
            ax.set_ylabel("Protein Group Name",fontsize=axisfont)
            ax.set_title(title,fontsize=titlefont)
            ax.set_axisbelow(True)
            ax.grid(linestyle="--")
            ax.margins(0.02)
            fig.set_tight_layout(True)

    # ====================================== PCA
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
                intensitydict[run]=searchoutput[searchoutput["Cond_Rep"]==run][["PG.ProteinGroups","PG.MS2Quantity"]].drop_duplicates().reset_index(drop=True).rename(columns={"PG.MS2Quantity":run}).set_index(keys="PG.ProteinGroups")
            df_intensity=[]
            for run in intensitydict.keys():
                temp_df=intensitydict[run]
                df_intensity.append(temp_df)
            concatenated_proteins=pd.concat(df_intensity,axis=1).dropna()

            X=np.array(concatenated_proteins).T
            pip=Pipeline([("scaler",StandardScaler()),("pca",PCA())]).fit(X)
            X_trans=pip.transform(X)
            #each row is a sample, each element of each row is a principal component

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

            ax1.legend(loc="upper left",bbox_to_anchor=[0,-0.1],fontsize=legendfont)

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

            #ax2.bar(np.arange(1,len(pip.named_steps.pca.explained_variance_ratio_)+1),pip.named_steps.pca.explained_variance_ratio_*100,edgecolor="k")
            ax2.bar(np.arange(1,4),pip.named_steps.pca.explained_variance_ratio_[:3]*100,edgecolor="k")
            ax2.set_xlabel("Principal Component",fontsize=axisfont)
            ax2.set_ylabel("Total % Variance Explained",fontsize=axisfont)
            #ax2.set_xticks(np.arange(1,len(pip.named_steps.pca.explained_variance_ratio_)+1))
            ax2.set_xticks(np.arange(1,4))
            ax2.set_axisbelow(True)
            ax2.grid(linestyle="--")
            ax2.tick_params(axis="both",labelsize=axisfont)

            fig.set_tight_layout(True)        

#endregion

# ============================================================================= Immunopeptidomics
#region
    # ====================================== Sequence Motifs
    @render.ui
    def seqmotif_run_ui():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
        opts=resultdf["Cond_Rep"].tolist()
        return ui.input_selectize("seqmotif_run_pick","Pick run:",choices=opts)
    #sequence motif plot
    @reactive.effect
    def _():
        @render.plot(width=input.seqmotif_width(),height=input.seqmotif_height())
        def seqmotif_plot():
            searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
            seq_df=searchoutput[searchoutput["Cond_Rep"]==input.seqmotif_run_pick()][["PEP.StrippedSequence"]].drop_duplicates()
            titlefont=input.titlefont()
            axisfont=input.axisfont()

            lengths=[]
            for pep in seq_df["PEP.StrippedSequence"].tolist():
                lengths.append(len(pep))
            seq_df["Peptide Length"]=lengths
            seq=seq_df[seq_df["Peptide Length"]==input.seqmotif_peplengths()].drop(columns=["Peptide Length"])["PEP.StrippedSequence"].tolist()

            matrix=lm.alignment_to_matrix(seq)
            if input.seqmotif_plottype()=="counts":
                ylabel="Counts"
            if input.seqmotif_plottype()=="information":
                matrix=lm.transform_matrix(matrix,from_type="counts",to_type="information")
                ylabel="Information (bits)"
            logo=lm.Logo(matrix,vsep=0.01,vpad=0.01,color_scheme="weblogo_protein")
            logo.ax.set_xlabel("Position",fontsize=axisfont)
            logo.ax.set_ylabel(ylabel,fontsize=axisfont)
            logo.ax.set_title(input.seqmotif_run_pick()+": "+str(input.seqmotif_peplengths())+"mers",fontsize=titlefont)
            logo.ax.set_ylim(bottom=0)

    # ====================================== Charge States (Bar)
    @reactive.calc
    def ipep_charge_peplength():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
        fillvalue="0"

        #run function by individual run
        dict_chargecountdf_run=dict()
        dict_peplengthcountdf_run=dict()

        for run in searchoutput["Cond_Rep"].drop_duplicates().tolist():
            df=searchoutput[searchoutput["Cond_Rep"]==run][["EG.ModifiedPeptide","FG.Charge","EG.ApexRT"]]
            charges=sorted(df["FG.Charge"].drop_duplicates(ignore_index=True))
            df_pivot=pd.pivot_table(df,index=["EG.ModifiedPeptide"],columns=["FG.Charge"],fill_value=fillvalue)

            chargedf=pd.DataFrame()
            chargedf["EG.ModifiedPeptide"]=df_pivot.index
            chargedf.set_index(["EG.ModifiedPeptide"],inplace=True)

            for charge in charges:
                #pivot table of just peptides of specific charge
                df_pivot_column=pd.DataFrame(df_pivot[('EG.ApexRT', charge)][df_pivot[('EG.ApexRT', charge)]!=fillvalue])
                #make an extra column of just the charge value
                df_pivot_column["Charge"]=[str(charge)]*len(df_pivot_column)
                #make an extra column in our final df to update from the initial pivot table
                chargedf["Charge"]=[fillvalue]*len(chargedf)
                #update the final df from the pivot table along same indices
                chargedf.update(df_pivot_column["Charge"])
                #change the name of the column so we can make the next one in the next loop
                chargedf=chargedf.rename(columns={"Charge":charge})

            #get list of charges present for peptides as a list
            chargelist=[]
            for pep in chargedf.index:
                listperpep=[]
                for item in chargedf.loc[pep].tolist():
                    if item!="0":
                        listperpep.append(item)
                    else:
                        pass
                chargelist.append(listperpep)
            #unpack each list as strings for better visualization and downstream use
            unpackedcharges=[]
            for ele in chargelist:
                if len(ele)==1:
                    unpackedcharges.append(ele[0])
                else:
                    placeholder=""
                    for i,string in enumerate(ele):
                        if i==0:
                            placeholder=placeholder+string
                        else:
                            placeholder=placeholder+","+string
                    unpackedcharges.append(placeholder)

            chargedf["list"]=unpackedcharges
            chargedf=chargedf.reset_index()
            chargegroups=sorted(chargedf["list"].drop_duplicates())

            #add in the StrippedSequence column
            strippedseq=searchoutput[searchoutput["Cond_Rep"]==run][["EG.ModifiedPeptide","PEP.StrippedSequence"]].drop_duplicates().sort_values("EG.ModifiedPeptide")
            chargedf["PEP.StrippedSequence"]=strippedseq["PEP.StrippedSequence"].reset_index(drop=True)

            #calculate peptide lengths
            lengthlist=[]
            for pep in chargedf["PEP.StrippedSequence"]:
                lengthlist.append(len(pep))
            chargedf["Peptide Length"]=lengthlist

            #df for plotting charge states only
            chargecountdf=pd.DataFrame(chargedf["list"].value_counts()).reset_index().sort_values("list").reset_index(drop=True)
            totals=sum(chargecountdf["count"])
            frequencies=[]
            for ele in chargecountdf["count"]:
                frequencies.append(round((ele/totals)*100,5))
            chargecountdf["frequency%"]=frequencies
            
            #df for plotting intersection of peptide length and charge state
            charge_length_df=chargedf[["list","Peptide Length"]]
            peplengths=list(set(charge_length_df["Peptide Length"]))
            peplengthcountdf=pd.DataFrame()
            peplengthcountdf["Peptide Length"]=peplengths
            for charge in chargecountdf["list"]:
                countpercharge=[]
                for peplength in peplengths:
                    val_count=charge_length_df[charge_length_df["Peptide Length"]==peplength]["list"].value_counts().get(charge)
                    if val_count is None:
                        countpercharge.append(0)
                    else:
                        countpercharge.append(val_count)
                peplengthcountdf[charge]=countpercharge
            
            #dump the chargedf and chargecountdf generated in the loop into a dict
            dict_chargecountdf_run[run]=chargecountdf
            dict_peplengthcountdf_run[run]=peplengthcountdf
            
        #run function by condition
        dict_chargecountdf_condition=dict()
        dict_peplengthcountdf_condition=dict()

        for run in sampleconditions:
            df=searchoutput[searchoutput["R.Condition"]==run][["EG.ModifiedPeptide","FG.Charge","EG.ApexRT"]]
            charges=sorted(df["FG.Charge"].drop_duplicates(ignore_index=True))
            df_pivot=pd.pivot_table(df,index=["EG.ModifiedPeptide"],columns=["FG.Charge"],fill_value=fillvalue)

            chargedf=pd.DataFrame()
            chargedf["EG.ModifiedPeptide"]=df_pivot.index
            chargedf.set_index(["EG.ModifiedPeptide"],inplace=True)

            for charge in charges:
                #pivot table of just peptides of specific charge
                df_pivot_column=pd.DataFrame(df_pivot[('EG.ApexRT', charge)][df_pivot[('EG.ApexRT', charge)]!=fillvalue])
                #make an extra column of just the charge value
                df_pivot_column["Charge"]=[str(charge)]*len(df_pivot_column)
                #make an extra column in our final df to update from the initial pivot table
                chargedf["Charge"]=[fillvalue]*len(chargedf)
                #update the final df from the pivot table along same indices
                chargedf.update(df_pivot_column["Charge"])
                #change the name of the column so we can make the next one in the next loop
                chargedf=chargedf.rename(columns={"Charge":charge})

            #get list of charges present for peptides as a list
            chargelist=[]
            for pep in chargedf.index:
                listperpep=[]
                for item in chargedf.loc[pep].tolist():
                    if item!="0":
                        listperpep.append(item)
                    else:
                        pass
                chargelist.append(listperpep)
            #unpack each list as strings for better visualization and downstream use
            unpackedcharges=[]
            for ele in chargelist:
                if len(ele)==1:
                    unpackedcharges.append(ele[0])
                else:
                    placeholder=""
                    for i,string in enumerate(ele):
                        if i==0:
                            placeholder=placeholder+string
                        else:
                            placeholder=placeholder+","+string
                    unpackedcharges.append(placeholder)

            chargedf["list"]=unpackedcharges
            chargedf=chargedf.reset_index()
            chargegroups=sorted(chargedf["list"].drop_duplicates())

            #add in the StrippedSequence column
            strippedseq=searchoutput[searchoutput["R.Condition"]==run][["EG.ModifiedPeptide","PEP.StrippedSequence"]].drop_duplicates().sort_values("EG.ModifiedPeptide")
            chargedf["PEP.StrippedSequence"]=strippedseq["PEP.StrippedSequence"].reset_index(drop=True)
            #calculate peptide lengths
            lengthlist=[]
            for pep in chargedf["PEP.StrippedSequence"]:
                lengthlist.append(len(pep))
            chargedf["Peptide Length"]=lengthlist

            #df for plotting charge states only
            chargecountdf=pd.DataFrame(chargedf["list"].value_counts()).reset_index().sort_values("list").reset_index(drop=True)
            totals=sum(chargecountdf["count"])
            frequencies=[]
            for ele in chargecountdf["count"]:
                frequencies.append(round((ele/totals)*100,5))
            chargecountdf["frequency%"]=frequencies
            
            #df for plotting intersection of peptide length and charge state
            charge_length_df=chargedf[["list","Peptide Length"]]
            peplengths=list(set(charge_length_df["Peptide Length"]))
            peplengthcountdf=pd.DataFrame()
            peplengthcountdf["Peptide Length"]=peplengths
            for charge in chargecountdf["list"]:
                countpercharge=[]
                for peplength in peplengths:
                    val_count=charge_length_df[charge_length_df["Peptide Length"]==peplength]["list"].value_counts().get(charge)
                    if val_count is None:
                        countpercharge.append(0)
                    else:
                        countpercharge.append(val_count)
                peplengthcountdf[charge]=countpercharge

            #dump the chargedf and chargecountdf generated in the loop into a dict
            dict_chargecountdf_condition[run]=chargecountdf
            dict_peplengthcountdf_condition[run]=peplengthcountdf

        return dict_chargecountdf_run,dict_peplengthcountdf_run,dict_chargecountdf_condition,dict_peplengthcountdf_condition
    @render.ui
    def chargestate_charges_ui():
        dict_chargecountdf_run,dict_peplengthcountdf_run,dict_chargecountdf_condition,dict_peplengthcountdf_condition=ipep_charge_peplength()
        if input.chargestate_peplength_condition_or_run()=="condition":
            plottingdf=dict_peplengthcountdf_condition
        if input.chargestate_peplength_condition_or_run()=="individual":
            plottingdf=dict_peplengthcountdf_run
        chargelist=[]
        for key in plottingdf.keys():
            chargelist.append(plottingdf[key].columns.tolist())
        chargelist=sorted(list(set(itertools.chain(*chargelist))))
        chargelist.remove("Peptide Length")

        return ui.input_checkbox_group("chargestate_charges","Charges to plot:",choices=chargelist)
    #bar chart of charge state counts
    @reactive.effect
    def _():
        @render.plot(width=input.charge_barchart_width(),height=input.charge_barchart_height())
        def charge_barchart():
            searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
            dict_chargecountdf_run,dict_peplengthcountdf_run,dict_chargecountdf_condition,dict_peplengthcountdf_condition=ipep_charge_peplength()
            if input.chargestate_bar_condition_or_run()=="condition":
                plottingdf=dict_chargecountdf_condition
                colors=colorpicker()
            if input.chargestate_bar_condition_or_run()=="individual":
                plottingdf=dict_chargecountdf_run
                colors=replicatecolors()

            titlefont=input.titlefont()
            axisfont=input.axisfont()

            if input.chargestate_charges_usepickedcharges()==True:
                chargelist=list(input.chargestate_charges())
                plottingdf_picked=dict()
                for key in plottingdf.keys():
                    plottingdf_picked[key]=plottingdf[key].set_index("list").loc[chargelist].reset_index()
                plottingdf=plottingdf_picked

            if len(plottingdf)==1:
                fig,ax=plt.subplots()
                key=list(plottingdf.keys())[0]
                x=np.arange(1,len(plottingdf[key]["list"])+1)
                ax.bar(x,plottingdf[key]["count"],edgecolor="k")
                ax.set_xticks(x,plottingdf[key]["list"],rotation=input.xaxis_label_rotation())
                ax.set_ylabel("Counts (%)",fontsize=axisfont)
                ax.set_xlabel("Charge(s)",fontsize=axisfont)
                ax.set_title(key,fontsize=titlefont)
                ax.set_axisbelow(True)
                ax.grid(linestyle="--")

            else:
                fig,ax=plt.subplots(ncols=len(plottingdf))

                for i,key in enumerate(plottingdf.keys()):
                    x=np.arange(1,len(plottingdf[key]["list"])+1)
                    if numconditions==1:
                        ax[i].bar(x,plottingdf[key]["count"],edgecolor="k",color=colorpicker())
                    else:
                        ax[i].bar(x,plottingdf[key]["count"],edgecolor="k",color=colors[i])
                    ax[i].set_xticks(x,plottingdf[key]["list"],rotation=input.xaxis_label_rotation())
                    ax[i].set_title(key,fontsize=titlefont)
                    ax[i].set_xlabel("Charge(s)",fontsize=axisfont)
                    ax[i].set_axisbelow(True)
                    ax[i].grid(linestyle="--")
                ax[0].set_ylabel("Counts",fontsize=axisfont)
            fig.set_tight_layout(True)

    # ====================================== Charge State (Stacked)
    #stacked bar chart of charge frequencies
    @reactive.effect
    def _():
        @render.plot(width=input.charge_stackedbarchart_width(),height=input.charge_stackedbarchart_height())
        def charge_stacked_barchart():
            dict_chargecountdf_run,dict_peplengthcountdf_run,dict_chargecountdf_condition,dict_peplengthcountdf_condition=ipep_charge_peplength()
            if input.chargestate_stacked_condition_or_run()=="condition":
                plottingdf=dict_chargecountdf_condition
            if input.chargestate_stacked_condition_or_run()=="individual":
                plottingdf=dict_chargecountdf_run

            titlefont=input.titlefont()
            axisfont=input.axisfont()

            fig,ax=plt.subplots()
            for i,key in enumerate(plottingdf.keys()):
                bottom=np.zeros(1)
                plottingdf[key]=plottingdf[key].sort_values("frequency%",ascending=False).reset_index(drop=True)
                for x in range(len(plottingdf[key])):
                    #generate a color list based on the length of each df in the dict
                    matplottabcolors=list(mcolors.TABLEAU_COLORS)
                    plotcolors=[]
                    if len(plottingdf[key]) > len(matplottabcolors):
                        dif=len(plottingdf[key])-len(matplottabcolors)
                        plotcolors=matplottabcolors
                        for y in range(dif):
                            plotcolors.append(matplottabcolors[y])
                    else:
                        plotcolors=matplottabcolors
                    ax.bar(i,plottingdf[key]["frequency%"][x],bottom=bottom,label=plottingdf[key]["list"][x],color=plotcolors[x])
                    bottom+=plottingdf[key]["frequency%"][x]
            ax.set_xticks(np.arange(0,len(plottingdf)),list(plottingdf.keys()),rotation=90)
            ax.set_ylabel("Frequency (%)",fontsize=axisfont)
            ax.set_xlabel("Condition",fontsize=axisfont)
            ax.set_axisbelow(True)
            ax.grid(linestyle="--")
            handles,labels=plt.gca().get_legend_handles_labels()
            by_label=OrderedDict(zip(labels,handles))
            ax.legend(by_label.values(), by_label.keys(),loc="center",bbox_to_anchor=(1.1,0.5))
    #table of frequencies for the stacked bar chart
    @render.data_frame
    def charge_stacked_table():
        dict_chargecountdf_run,dict_peplengthcountdf_run,dict_chargecountdf_condition,dict_peplengthcountdf_condition=ipep_charge_peplength()
        if input.chargestate_stacked_condition_or_run()=="condition":
            plottingdf=dict_chargecountdf_condition
        if input.chargestate_stacked_condition_or_run()=="individual":
            plottingdf=dict_chargecountdf_run
        displaydf=pd.DataFrame()
        for i,key in enumerate(plottingdf.keys()):
            displaydf=pd.concat([displaydf,plottingdf[key][["list","frequency%"]].sort_values("frequency%",ascending=False).rename(columns={"list":key,"frequency%":"frequency%_"+str(i)})],axis=1)

        return render.DataGrid(displaydf,editable=False)

    # ====================================== Charge State/Peptide Length
    @render.ui
    def chargestate_peplength_plotrange_ui():
        dict_chargecountdf_run,dict_peplengthcountdf_run,dict_chargecountdf_condition,dict_peplengthcountdf_condition=ipep_charge_peplength()
        if input.chargestate_peplength_condition_or_run()=="condition":
            plottingdf=dict_peplengthcountdf_condition
        if input.chargestate_peplength_condition_or_run()=="individual":
            plottingdf=dict_peplengthcountdf_run

        min=7
        max=30
        
        return ui.input_slider("chargestate_peplength_plotrange","Plot Range",min=1,max=50,value=[min,max],step=1,ticks=True,width="300px",drag_range=True)
    @render.ui
    def chargestate_peplength_charges_ui():
        dict_chargecountdf_run,dict_peplengthcountdf_run,dict_chargecountdf_condition,dict_peplengthcountdf_condition=ipep_charge_peplength()
        if input.chargestate_peplength_condition_or_run()=="condition":
            plottingdf=dict_peplengthcountdf_condition
        if input.chargestate_peplength_condition_or_run()=="individual":
            plottingdf=dict_peplengthcountdf_run
        chargelist=[]
        for key in plottingdf.keys():
            chargelist.append(plottingdf[key].columns.tolist())
        chargelist=sorted(list(set(itertools.chain(*chargelist))))
        chargelist.remove("Peptide Length")

        return ui.input_checkbox_group("chargestate_peplength_charges","Charges to plot:",choices=chargelist)
    #plot charge states per peptide length
    @reactive.effect
    def _():
        @render.plot(width=input.chargestate_peplength_width(),height=input.chargestate_peplength_height())
        def chargestate_peplength():
            dict_chargecountdf_run,dict_peplengthcountdf_run,dict_chargecountdf_condition,dict_peplengthcountdf_condition=ipep_charge_peplength()
            if input.chargestate_peplength_condition_or_run()=="condition":
                plottingdf=dict_peplengthcountdf_condition
            if input.chargestate_peplength_condition_or_run()=="individual":
                plottingdf=dict_peplengthcountdf_run

            axisfont=input.axisfont()
            titlefont=input.titlefont()

            if len(plottingdf)==1:
                fig,ax=plt.subplots()
                key=list(plottingdf.keys())[0]
                plotdf=plottingdf[key].set_index("Peptide Length")
                if input.usepickedcharges()==True:
                    columns=input.chargestate_peplength_charges()
                else:
                    columns=plotdf.columns.tolist()
                x=plotdf.index.tolist()
                bottom=np.zeros(len(plotdf))
                for col in columns:
                    ax.bar(x,plotdf[col],label=col)
                    bottom+=plotdf[col].tolist()
                ax.set_xlabel("Peptide Length",fontsize=axisfont)
                ax.set_title(key,fontsize=titlefont)
                ax.legend(loc="upper right",prop={'size':8})
                ax.set_axisbelow(True)
                ax.grid(linestyle="--")
                ax.set_ylabel("Counts",fontsize=axisfont)
                ax.set_xlim(left=input.chargestate_peplength_plotrange()[0]-0.75,right=input.chargestate_peplength_plotrange()[1]+0.5)
                ax.xaxis.set_major_locator(MaxNLocator(integer=True))
                ax.xaxis.set_minor_locator(MultipleLocator(1))
                fig.set_tight_layout(True)

            else:
                fig,ax=plt.subplots(ncols=len(plottingdf))
                for i,key in enumerate(plottingdf.keys()):
                    plotdf=plottingdf[key].set_index("Peptide Length")
                    if input.usepickedcharges()==True:
                        columns=input.chargestate_peplength_charges()
                    else:
                        columns=plotdf.columns.tolist()
                    x=plotdf.index.tolist()
                    bottom=np.zeros(len(plotdf))
                    for col in columns:
                        ax[i].bar(x,plotdf[col],label=col,bottom=bottom)
                        bottom+=plotdf[col].tolist()

                    ax[i].set_xlabel("Peptide Length",fontsize=axisfont)
                    ax[i].set_title(key,fontsize=titlefont)
                    ax[i].legend(loc="upper right",prop={'size':8})
                    ax[i].set_axisbelow(True)
                    ax[i].grid(linestyle="--")
                    ax[i].set_xlim(left=input.chargestate_peplength_plotrange()[0]-0.75,right=input.chargestate_peplength_plotrange()[1]+0.5)
                    ax[i].xaxis.set_major_locator(MaxNLocator(integer=True))
                    ax[i].xaxis.set_minor_locator(MultipleLocator(1))

                ax[0].set_ylabel("Counts",fontsize=axisfont)
                fig.set_tight_layout(True)

#endregion

# ============================================================================= Mixed Proteome
#region

    # ====================================== Info
    #show a table of the detected organisms and an order column to reorder them 
    @render.data_frame
    def organismtable():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
        organismlist=[]
        for entry in searchoutput["PG.ProteinNames"].drop_duplicates().str.split("_"):
            organismlist.append(entry[-1])
        organism_table=pd.DataFrame()
        organism_table["Organism"]=list(set(organismlist))
        organism_table["Order"]=np.arange(1,len(organism_table["Organism"])+1).astype(str)
        for column in searchoutput["R.Condition"].drop_duplicates().reset_index(drop=True):
            organism_table[column+"_Quant Ratio"]=""
        return render.DataGrid(organism_table,editable=True,width="100%")
    #take the view of organismtable and generate organismlist in the order specified
    @reactive.calc
    def organism_list_from_table():
        organism_table_view=organismtable.data_view()
        organismlist=list(organism_table_view.sort_values("Order")["Organism"])
        return organismlist
    #generate dfs for ID counts and summed intensities per organism
    @reactive.calc
    def mixedproteomestats():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
        organismlist=organism_list_from_table()

        mixedproteomecounts=pd.DataFrame()
        mixedproteomecounts["Cond_Rep"]=resultdf["Cond_Rep"]
        mixedproteomeintensity=pd.DataFrame()
        mixedproteomeintensity["Cond_Rep"]=resultdf["Cond_Rep"]

        for organism in organismlist:
            proteincountlist=[]
            peptidecountlist=[]
            precursorcountlist=[]
            summedintensitylist=[]
            for run in resultdf["Cond_Rep"]:
                df=searchoutput[searchoutput["Cond_Rep"]==run]
                summedintensitylist.append(df[df["PG.ProteinNames"].str.contains(organism)]["PG.MS2Quantity"].drop_duplicates().reset_index(drop=True).sum())
                proteincountlist.append(df[(df["PG.ProteinNames"].str.contains(organism))&(df["PG.MS2Quantity"]>0)]["PG.ProteinNames"].drop_duplicates().reset_index(drop=True).count())
                peptidecountlist.append(df[(df["PG.ProteinNames"].str.contains(organism))&(df["FG.MS2Quantity"]>0)]["EG.ModifiedPeptide"].drop_duplicates().reset_index(drop=True).count())
                precursorcountlist.append(len(df[(df["PG.ProteinNames"].str.contains(organism))&(df["FG.MS2Quantity"]>0)][["EG.ModifiedPeptide","FG.Charge"]].drop_duplicates().reset_index(drop=True)))
            mixedproteomeintensity[organism+"_summedintensity"]=summedintensitylist
            mixedproteomecounts[organism+"_proteins"]=proteincountlist
            mixedproteomecounts[organism+"_peptides"]=peptidecountlist
            mixedproteomecounts[organism+"_precursors"]=precursorcountlist
        
        return mixedproteomecounts,mixedproteomeintensity

    # ====================================== Counts per Organism
    #counts per organism
    @reactive.effect
    def _():
        @render.plot(width=input.countsperorganism_width(),height=input.countsperorganism_height())
        def countsperorganism():
            mixedproteomecounts,mixedproteomeintensity=mixedproteomestats()
            organismlist=organism_list_from_table()

            titlefont=input.titlefont()
            axisfont=input.axisfont()
            labelfont=input.labelfont()
            legendfont=input.legendfont()
            y_padding=input.ypadding()

            matplottabcolors=list(mcolors.TABLEAU_COLORS)
            bluegray_colors=["#054169","#0071BC","#737373"]

            if input.coloroptions_sumint()=="matplot":
                colors=matplottabcolors
            elif input.coloroptions_sumint()=="bluegray":
                colors=bluegray_colors

            if input.countsplotinput()=="proteins":
                titleprop="Protein"
            if input.countsplotinput()=="peptides":
                titleprop="Peptide"
            if input.countsplotinput()=="precursors":
                titleprop="Precursor"

            x=np.arange(len(mixedproteomecounts["Cond_Rep"].tolist()))
            width=0.25

            relevantcolumns=[col for col in mixedproteomecounts if input.countsplotinput() in col]
            maxvalue=mixedproteomecounts[relevantcolumns].values.max()

            fix,ax=plt.subplots()
            for i in range(len(organismlist)):
                ax.bar(x+(i*width),mixedproteomecounts[organismlist[i]+"_"+input.countsplotinput()],width=width,label=organismlist[i],color=colors[i])
                ax.bar_label(ax.containers[i],label_type="edge",rotation=90,padding=5,fontsize=labelfont)
            ax.set_xticks(x+width,mixedproteomecounts["Cond_Rep"].tolist(),rotation=input.xaxis_label_rotation())
            ax.set_ylim(top=maxvalue+(y_padding*maxvalue))
            ax.legend(loc='center left',bbox_to_anchor=(1, 0.5),prop={'size':legendfont})
            ax.set_ylabel("Counts",fontsize=axisfont)
            ax.set_xlabel("Condition",fontsize=axisfont)
            ax.set_title(titleprop+" Counts per Organism",fontsize=titlefont)
            ax.set_axisbelow(True)
            ax.grid(linestyle="--")

    # ====================================== Summed Intensities
    #summed intensities per organism per run
    @reactive.effect
    def _():
        @render.plot(width=input.summedintensities_width(),height=input.summedintensities_height())
        def summedintensities():
            mixedproteomecounts,mixedproteomeintensity=mixedproteomestats()
            organismlist=organism_list_from_table()

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

            x=np.arange(len(mixedproteomeintensity["Cond_Rep"].tolist()))
            bottom=np.zeros(len(mixedproteomeintensity["Cond_Rep"].tolist()))
            fig,ax=plt.subplots()
            for i in range(len(organismlist)):
                ax.bar(x,mixedproteomeintensity[organismlist[i]+"_summedintensity"],bottom=bottom,label=organismlist[i],color=colors[i])
                bottom+=mixedproteomeintensity[organismlist[i]+"_summedintensity"].tolist()

            ax.set_xticks(x,labels=mixedproteomecounts["Cond_Rep"].tolist(),rotation=input.xaxis_label_rotation())
            ax.set_ylabel("Total Intensity",fontsize=axisfont)
            ax.set_xlabel("Condition",fontsize=axisfont)
            ax.legend(loc="center left",bbox_to_anchor=(1, 0.5),fontsize=legendfont)
            ax.set_axisbelow(True)
            ax.grid(linestyle="--")
            ax.set_title("Total Intensity per Organism per Run",fontsize=titlefont)

    # ====================================== Quant Ratios
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
    #quant ratios
    @reactive.effect
    def _():
        @render.plot(width=input.quantratios_width(),height=input.quantratios_height())
        def quantratios():
            searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
            organismlist=organism_list_from_table()
            organism_table=organismtable.data_view()

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

            referencecondition=input.referencecondition_list()
            testcondition=input.testcondition_list()

            testcolumn=organism_table[[col for col in organism_table if testcondition in col]].columns[0]
            referencecolumn=organism_table[[col for col in organism_table if referencecondition in col]].columns[0]

            testratios=organism_table.sort_values("Order")[testcolumn].astype(int).tolist()
            referenceratios=organism_table.sort_values("Order")[referencecolumn].astype(int).tolist()
            
            organism_merged=dict()
            ratio_average=pd.DataFrame()
            ratio_average["Organism"]=organismlist

            if input.y_log_scale()=="log2":
                ratio_average["Theoretical_Ratio"]=[np.log2(i/j) for i,j in zip(testratios,referenceratios)]
            if input.y_log_scale()=="log10":
                ratio_average["Theoretical_Ratio"]=[np.log10(i/j) for i,j in zip(testratios,referenceratios)]
            averagelist=[]

            for organism in organismlist:
                df=searchoutput[(searchoutput["Cond_Rep"].str.contains(referencecondition))&(searchoutput["PG.ProteinNames"].str.contains(organism))][["PG.ProteinNames","PG.MS2Quantity"]].drop_duplicates().reset_index(drop=True)
                if input.quantratios_mean_median()=="mean":
                    df_reference=df.groupby(["PG.ProteinNames"]).mean().reset_index().rename(columns={"PG.MS2Quantity":referencecondition})
                if input.quantratios_mean_median()=="median":
                    df_reference=df.groupby(["PG.ProteinNames"]).median().reset_index().rename(columns={"PG.MS2Quantity":referencecondition})

                df_reference[referencecondition+"_stdev"]=df.groupby(["PG.ProteinNames"]).std().reset_index(drop=True)
                df_reference[referencecondition+"_CV"]=df_reference[referencecondition+"_stdev"]/df_reference[referencecondition]*100
                
                df=searchoutput[(searchoutput["Cond_Rep"].str.contains(testcondition))&(searchoutput["PG.ProteinNames"].str.contains(organism))][["PG.ProteinNames","PG.MS2Quantity"]].drop_duplicates().reset_index(drop=True)
                if input.quantratios_mean_median()=="mean":
                    df_test=df.groupby(["PG.ProteinNames"]).mean().reset_index().rename(columns={"PG.MS2Quantity":testcondition})
                if input.quantratios_mean_median()=="median":
                    df_test=df.groupby(["PG.ProteinNames"]).median().reset_index().rename(columns={"PG.MS2Quantity":testcondition})

                df_test[testcondition+"_stdev"]=df.groupby(["PG.ProteinNames"]).std().reset_index(drop=True)
                df_test[testcondition+"_CV"]=df_test[testcondition+"_stdev"]/df_test[testcondition]*100
                
                if 1 in maxreplicatelist:
                    merged=df_reference.merge(df_test,how="inner")
                else:
                    merged=df_reference.merge(df_test,how="inner").dropna()

                if input.x_log_scale()=="log2":
                    merged["reference"]=np.log2(merged[referencecondition])
                if input.x_log_scale()=="log10":
                    merged["reference"]=np.log10(merged[referencecondition])
                if input.y_log_scale()=="log2":
                    merged["ratio"]=np.log2(merged[testcondition]/merged[referencecondition])
                if input.y_log_scale()=="log10":
                    merged["ratio"]=np.log10(merged[testcondition]/merged[referencecondition])

                averagelist.append(np.average(merged["ratio"].dropna()))

                organism_merged[organism]=merged

                if input.cvcutoff_switch()==True:
                    cv_cutoff=input.cvcutofflevel()
                    organism_merged[organism]=organism_merged[organism][(organism_merged[organism][referencecondition+"_CV"]<cv_cutoff)&(organism_merged[organism][testcondition+"_CV"]<cv_cutoff)]

            ratio_average["Experimental_Ratio"]=averagelist

            fig,ax=plt.subplots(nrows=1,ncols=3,gridspec_kw={"width_ratios":[2,5,2]})
            fig.set_tight_layout(True)
            for x,organism in enumerate(organismlist):
                ax[0].bar(x,len(organism_merged[organism]),color=colors[x])
                ax[0].bar_label(ax[0].containers[x],label_type="edge",rotation=90,padding=5,fontsize=labelfont)
                ax[1].scatter(organism_merged[organism]["reference"],organism_merged[organism]["ratio"],alpha=0.25,color=colors[x])
                ax[2].hist(organism_merged[organism]["ratio"],bins=100,orientation=u"horizontal",alpha=0.5,density=True,color=colors[x])

            for x in range(len(organismlist)):
                ax[x].set_axisbelow(True)
                ax[x].grid(linestyle="--")
                ax[1].axhline(y=ratio_average["Experimental_Ratio"][x],linestyle="dashed",color=colors[x])
                ax[2].axhline(y=ratio_average["Experimental_Ratio"][x],linestyle="dashed",color=colors[x])
                ax[1].axhline(y=ratio_average["Theoretical_Ratio"][x],color=colors[x])
                ax[2].axhline(y=ratio_average["Theoretical_Ratio"][x],color=colors[x])

            if input.plotrange_switch()==True:
                ymin=input.plotrange()[0]
                ymax=input.plotrange()[1]
                ax[1].set_ylim(ymin,ymax)
                ax[2].set_ylim(ymin,ymax)

            ax[0].set_xticks(np.arange(len(organismlist)),organismlist,rotation=input.xaxis_label_rotation())
            ax[0].set_ylabel("Number of Proteins",fontsize=axisfont)
            bottom,top=ax[0].get_ylim()
            ax[0].set_ylim(top=top+(0.15*top))

            leg=ax[1].legend(organismlist,loc="upper right",prop={'size':legendfont})
            for tag in leg.legend_handles:
                tag.set_alpha(1)
            ax[1].set_xlabel(input.x_log_scale()+" Intensity, Reference",fontsize=axisfont)
            ax[1].set_ylabel(input.y_log_scale()+" Ratio, Test/Reference",fontsize=axisfont)
            ax[1].set_title("Reference: "+referencecondition+", Test: "+testcondition,pad=10,fontsize=titlefont)

            ax[2].set_xlabel("Density",fontsize=axisfont)
            ax[2].set_ylabel(input.y_log_scale()+" Ratio, Test/Reference",fontsize=axisfont)
    #show table of quant ratios
    @render.table
    def quantratios_table():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
        organismlist=organism_list_from_table()
        organism_table=organismtable.data_view()

        referencecondition=input.referencecondition_list()
        testcondition=input.testcondition_list()

        testcolumn=organism_table[[col for col in organism_table if testcondition in col]].columns[0]
        referencecolumn=organism_table[[col for col in organism_table if referencecondition in col]].columns[0]

        testratios=organism_table.sort_values("Order")[testcolumn].astype(int).tolist()
        referenceratios=organism_table.sort_values("Order")[referencecolumn].astype(int).tolist()
        
        organism_merged=dict()
        ratio_average=pd.DataFrame()
        ratio_average["Organism"]=organismlist
        
        if input.y_log_scale()=="log2":
            ratio_average["Theoretical_Ratio (log2)"]=[np.log2(i/j) for i,j in zip(testratios,referenceratios)]
        if input.y_log_scale()=="log10":
            ratio_average["Theoretical_Ratio (log10)"]=[np.log10(i/j) for i,j in zip(testratios,referenceratios)]

        averagelist=[]

        for organism in organismlist:
            df=searchoutput[(searchoutput["Cond_Rep"].str.contains(referencecondition))&(searchoutput["PG.ProteinNames"].str.contains(organism))][["PG.ProteinNames","PG.MS2Quantity"]].drop_duplicates().reset_index(drop=True)
            if input.quantratios_mean_median()=="mean":
                df_reference=df.groupby(["PG.ProteinNames"]).mean().reset_index().rename(columns={"PG.MS2Quantity":referencecondition})
            if input.quantratios_mean_median()=="median":
                df_reference=df.groupby(["PG.ProteinNames"]).median().reset_index().rename(columns={"PG.MS2Quantity":referencecondition})
            df_reference[referencecondition+"_stdev"]=df.groupby(["PG.ProteinNames"]).std().reset_index(drop=True)
            df_reference[referencecondition+"_CV"]=df_reference[referencecondition+"_stdev"]/df_reference[referencecondition]*100
            
            df=searchoutput[(searchoutput["Cond_Rep"].str.contains(testcondition))&(searchoutput["PG.ProteinNames"].str.contains(organism))][["PG.ProteinNames","PG.MS2Quantity"]].drop_duplicates().reset_index(drop=True)
            if input.quantratios_mean_median()=="mean":
                df_test=df.groupby(["PG.ProteinNames"]).mean().reset_index().rename(columns={"PG.MS2Quantity":testcondition})
            if input.quantratios_mean_median()=="median":
                df_test=df.groupby(["PG.ProteinNames"]).median().reset_index().rename(columns={"PG.MS2Quantity":testcondition})
            df_test[testcondition+"_stdev"]=df.groupby(["PG.ProteinNames"]).std().reset_index(drop=True)
            df_test[testcondition+"_CV"]=df_test[testcondition+"_stdev"]/df_test[testcondition]*100
            
            if 1 in maxreplicatelist:
                merged=df_reference.merge(df_test,how="inner")
            else:
                merged=df_reference.merge(df_test,how="inner").dropna()

            if input.y_log_scale()=="log2":
                merged["ratio"]=np.log2(merged[testcondition]/merged[referencecondition])
            if input.y_log_scale()=="log10":
                merged["ratio"]=np.log10(merged[testcondition]/merged[referencecondition])
            averagelist.append(np.average(merged["ratio"].dropna()))

            organism_merged[organism]=merged

            if input.cvcutoff_switch()==True:
                cv_cutoff=input.cvcutofflevel()
                organism_merged[organism]=organism_merged[organism][(organism_merged[organism][referencecondition+"_CV"]<cv_cutoff)&(organism_merged[organism][testcondition+"_CV"]<cv_cutoff)]
            
        ratio_average["Experimental_Ratio ("+input.y_log_scale()+")"]=averagelist
        return ratio_average

#endregion

# ============================================================================= PRM
#region

    # ====================================== PRM List
    #download PRM table template
    @render.download(filename="prm_template.csv")
    def prm_template():
        template_df=pd.DataFrame(columns=[
            "PG.ProteinGroups",
            "EG.ModifiedPeptide"
            ])
        with io.BytesIO() as buf:
            template_df.to_csv(buf,index=False)
            yield buf.getvalue()
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

    # ====================================== PRM Table
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
            prm_peptide=searchoutput[searchoutput["EG.ModifiedPeptide"]==peptide][["PG.ProteinGroups","EG.ModifiedPeptide","FG.PrecMz","FG.Charge","EG.ApexRT","EG.IonMobility"]].groupby(["PG.ProteinGroups","EG.ModifiedPeptide","FG.Charge"]).mean().reset_index()
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

        searchoutput_prm=searchoutput_prm[["Mass [m/z]","Charge","Isolation Width [m/z]","RT [s]","RT Range [s]","Start IM [1/k0]","End IM [1/k0]","CE [eV]","External ID","Description","PG.ProteinGroups","EG.ModifiedPeptide","EG.IonMobility"]]

        searchoutput_prm.drop(columns=["PG.ProteinGroups","EG.ModifiedPeptide","EG.IonMobility"],inplace=True)

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

    # ====================================== Individual Tracker
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
            #make sure the chargelist is sorted so we're plotting in charge order
            chargelist.sort()

            titlefont=input.titlefont()
            width=0.25

            #make a table of expected values for the concentration ratios
            df=searchoutput[["R.Condition","Concentration"]].drop_duplicates().reset_index(drop=True)
            expectedratio=[]
            for i in range(len(df)):
                conc_min=min(df["Concentration"])
                expectedratio.append(df["Concentration"][i]/conc_min)
            df["Expected Ratio"]=expectedratio

            fig,ax=plt.subplots(ncols=2,nrows=2)
            fig.set_tight_layout(True)
            for i,charge in enumerate(chargelist):
                meandf=pepdf[pepdf["FG.Charge"]==charge][["R.Condition","FG.MS2Quantity"]].groupby("R.Condition",sort=False).mean()
                stdev=pepdf[pepdf["FG.Charge"]==charge][["R.Condition","FG.MS2Quantity"]].groupby("R.Condition",sort=False).std()
                cv=stdev/meandf*100
                meandf=meandf.reset_index()
                stdev=stdev.reset_index()
                cv=cv.reset_index()
                detectedinreps=pd.DataFrame({"Count":pepdf[pepdf["FG.Charge"]==charge].groupby("R.Condition",sort=False).size()}).reset_index()

                if len(meandf)<len(searchoutput["R.Condition"].drop_duplicates().reset_index(drop=True)):
                    expectedrows=pd.DataFrame({"R.Condition":searchoutput["R.Condition"].drop_duplicates().reset_index(drop=True)})
                    meandf=expectedrows.merge(meandf,how="left",left_on="R.Condition",right_on="R.Condition").fillna(0)
                    stdev=expectedrows.merge(stdev,how="left",left_on="R.Condition",right_on="R.Condition").fillna(0)
                    cv=expectedrows.merge(cv,how="left",left_on="R.Condition",right_on="R.Condition").fillna(0)
                    detectedinreps=expectedrows.merge(detectedinreps,how="left",left_on="R.Condition",right_on="R.Condition").fillna(0)

                x=np.arange(0,len(meandf["R.Condition"]),1)
                y=meandf["FG.MS2Quantity"].tolist()
                fit=np.poly1d(np.polyfit(x,y,1))
                ax[0,0].errorbar(x,y,yerr=stdev["FG.MS2Quantity"],marker="o",linestyle="None")
                ax[0,0].plot(x,fit(x),linestyle="--",color="black")
                ax[1,0].plot(meandf["R.Condition"],cv["FG.MS2Quantity"],marker="o")
                ax[0,1].bar(x+i*width,detectedinreps["Count"],width=width,label=str(charge)+"+")
                if "Concentration" in searchoutput.columns:
                    #use a single dataframe to plot the expected and measured ratios for the selected peptides
                    merged=df.merge(meandf)
                    min_conc_signal=merged.loc[merged["Concentration"]==min(merged["Concentration"]),"FG.MS2Quantity"].values[0]
                    measuredratio=[]
                    #if there's no signal for the lowest concentration condition, set measured ratio values to zero since the numbers won't be informative
                    if min_conc_signal!=0:
                        for conc in merged["Concentration"]:
                            measuredratio.append(merged.loc[merged["Concentration"]==conc,"FG.MS2Quantity"].values[0]/min_conc_signal)
                    else:
                        measuredratio.append([0.0]*len(merged["Concentration"]))
                        measuredratio=list(itertools.chain(*measuredratio))
                    merged["Measured Ratio"]=measuredratio
                    #plotting average FG.MS2Quantity over each condition
                    ax[1,1].scatter(merged["Expected Ratio"],merged["Measured Ratio"])
                else:
                    ax[1,1].set_visible(False)
                
            ax[0,0].set_ylabel("FG.MS2Quantity")
            ax[0,0].set_xticks(x)
            ax[0,0].set_xticklabels(searchoutput["R.Condition"].drop_duplicates().reset_index(drop=True),rotation=input.xaxis_label_rotation())
            ax[0,0].set_ylim(bottom=-(ax[0,0].get_ylim()[1])/10)
            ax[0,0].set_title("Intensity Across Runs")
            ax[0,0].set_axisbelow(True)
            ax[0,0].grid(linestyle="--")

            ax[1,0].axhline(y=20,linestyle="--",color="black")
            ax[1,0].set_xticks(x)
            ax[1,0].set_xticklabels(searchoutput["R.Condition"].drop_duplicates().reset_index(drop=True),rotation=input.xaxis_label_rotation())
            ax[1,0].set_ylabel("CV (%)")
            ax[1,0].set_title("CVs")
            ax[1,0].set_axisbelow(True)
            ax[1,0].grid(linestyle="--")

            ax[0,1].set_ylabel("Number of Replicates")
            ax[0,1].set_xticks(x,meandf["R.Condition"],rotation=input.xaxis_label_rotation())
            ax[0,1].set_title("Number of Replicates Observed")
            ax[0,1].set_axisbelow(True)
            ax[0,1].grid(linestyle="--")

            ax[1,1].set_xlabel("Expected Ratio")
            ax[1,1].set_ylabel("Measured Ratio")
            lims=[np.min([ax[1,1].get_xlim(),ax[1,1].get_ylim()]),np.max([ax[1,1].get_xlim(),ax[1,1].get_ylim()])]
            ax[1,1].plot(lims,lims,color="k",linestyle="--",alpha=0.5)
            ax[1,1].set_title("Dilution Curve")
            ax[1,1].set_axisbelow(True)
            ax[1,1].grid(linestyle="--")

            fig.legend(loc="lower right",bbox_to_anchor=(0.99,0.9))
            fig.suptitle(peptide.strip("_"),fontsize=titlefont)
            fig.set_tight_layout(True)

    # ====================================== Intensity Across Runs
    #plot intensity of all prm peptides across runs
    @reactive.effect
    def _():
        @render.plot(width=input.prmpepintensity_width(),height=input.prmpepintensity_height())
        def prmpepintensity_plot():
            searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
            prm_list,searchoutput_prmpepts=prm_import()

            axisfont=input.axisfont()
            legendfont=input.legendfont()

            fig,ax=plt.subplots()
            for peptide in prm_list["EG.ModifiedPeptide"]:
                pepdf=searchoutput_prmpepts[searchoutput_prmpepts["EG.ModifiedPeptide"]==peptide]
                chargelist=pepdf["FG.Charge"].drop_duplicates().tolist()

                for charge in chargelist:
                    plottingdf=pepdf[pepdf["FG.Charge"]==charge][["Cond_Rep","FG.Charge","FG.MS2Quantity"]]

                    if len(plottingdf)<len(searchoutput["Cond_Rep"].drop_duplicates().reset_index(drop=True)):
                        expectedrows=pd.DataFrame({"Cond_Rep":searchoutput["Cond_Rep"].drop_duplicates().reset_index(drop=True)})
                        plottingdf=expectedrows.merge(plottingdf,how="left",left_on="Cond_Rep",right_on="Cond_Rep").fillna(1)
                    else:
                        pass
                    ax.plot(plottingdf["Cond_Rep"],np.log10(plottingdf["FG.MS2Quantity"]),marker="o",label=peptide.strip("_")+"_"+str(charge)+"+")

            ax.legend(loc='center left', bbox_to_anchor=(1,0.5),prop={'size':legendfont})
            ax.tick_params(axis="x",rotation=input.xaxis_label_rotation(),labelsize=axisfont)
            ax.tick_params(axis="y",labelsize=axisfont)
            ax.set_xlabel("Condition",fontsize=axisfont)
            ax.set_ylabel("log10(FG.MS2Quantity)",fontsize=axisfont)
            ax.set_axisbelow(True)
            ax.grid(linestyle="--")

#endregion

# ============================================================================= Dilution Series
#region
    #ui call to pick normalizing condition for dilution series calculations
    @render.ui
    def normalizingcondition():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
        opts=sampleconditions
        return ui.input_selectize("normalizingcondition_pick","Pick normalizing condition",choices=opts)

    #dilution series calculations for plotting
    @reactive.calc
    def dilutionseries_calc():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
        sortedconditions=[]
        concentrations=searchoutput["Concentration"].drop_duplicates().tolist()
        sortedconcentrations=sorted(concentrations)
        for i in sortedconcentrations:
            sortedconditions.append(searchoutput[searchoutput["Concentration"]==i]["R.Condition"].values[0])

        normalizingcondition=input.normalizingcondition_pick()

        dilutionseries=[]
        theoreticalratio=[]
        norm=searchoutput[searchoutput["R.Condition"]==normalizingcondition][["PG.ProteinGroups","PG.MS2Quantity"]].groupby("PG.ProteinGroups").mean().reset_index()

        for condition in sortedconditions:
            test=searchoutput[searchoutput["R.Condition"]==condition][["PG.ProteinGroups","PG.MS2Quantity"]].groupby("PG.ProteinGroups").mean().reset_index()
            merge=norm.merge(test,how="left",on="PG.ProteinGroups",suffixes=("_norm","_test"))
            merge["Ratio"]=merge["PG.MS2Quantity_test"]/merge["PG.MS2Quantity_norm"]
            merge=merge.dropna()
            dilutionseries.append(merge["Ratio"])
            
            norm_conc=searchoutput[searchoutput["R.Condition"]==normalizingcondition]["Concentration"].drop_duplicates().reset_index(drop=True)[0]
            conc=searchoutput[searchoutput["R.Condition"]==condition]["Concentration"].drop_duplicates().reset_index(drop=True)[0]
            theoreticalratio.append(conc/norm_conc)
        
        return sortedconditions,dilutionseries,theoreticalratio

    #plot dilution ratios
    @reactive.effect
    def _():
        @render.plot(width=input.dilutionseries_width(),height=input.dilutionseries_height())
        def dilutionseries_plot(width=input.dilutionseries_width(),height=input.dilutionseries_height()):
            sortedconditions,dilutionseries,theoreticalratio=dilutionseries_calc()
            axisfont=input.axisfont()

            fig,ax=plt.subplots()

            medianlineprops=dict(linestyle="--",color="black")
            flierprops=dict(markersize=3)

            bplot=ax.boxplot(dilutionseries,medianprops=medianlineprops,flierprops=flierprops)
            plot=ax.violinplot(dilutionseries,showextrema=False)
            ax.plot(np.arange(1,len(sortedconditions)+1,1),theoreticalratio,zorder=2.5,marker="o",color="k",label="Theoretical Ratio")

            ax.set_yscale("log")
            ax.set_xticks(np.arange(1,len(sortedconditions)+1,1),labels=sortedconditions,rotation=input.xaxis_label_rotation())
            ax.set_xlabel("Condition",fontsize=axisfont)
            ax.set_ylabel("Ratio",fontsize=axisfont)
            ax.set_axisbelow(True)
            ax.grid(linestyle="--")
            ax.legend(loc="upper left")

            colors=colorpicker()
            for z,color in zip(plot["bodies"],colors):
                z.set_facecolor(color)
                z.set_edgecolor("black")
                z.set_alpha(0.7)   

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
        
        resultdf_glyco=pd.DataFrame(searchoutput[["Cond_Rep","R.Condition","R.Replicate"]].drop_duplicates()).reset_index(drop=True)
        num_glycoproteins=[]
        num_glycopeptides=[]
        num_glycoPSMs=[]
        dict_glycoproteins=dict()
        dict_glycopeptides=dict()
        dict_glycoPSMs=dict()
        for run in searchoutput["Cond_Rep"].drop_duplicates():
            df=searchoutput[searchoutput["Cond_Rep"]==run]

            #filtered PSMs with a q value cutoff (used for the dfs generated here)
            if input.software()=="fragpipe_glyco":
                df=df[(df["Glycan q-value"].isnull()==False)&(df["Glycan q-value"]<=0.01)]
            if input.software()=="glycoscape":
                df=df[df["Total Glycan Composition"].isnull()==False]

            #Assign truth value to whether number after Hex mod is 5<x<10
            highmannose=[]
            for i in range(len(df["Total Glycan Composition"].tolist())):
                glycanstring=str(df["Total Glycan Composition"].tolist()[i])
                if "Hex(" in glycanstring:
                    hexvalue=df["Total Glycan Composition"].tolist()[i][df["Total Glycan Composition"].tolist()[i].find("Hex(")+len("Hex(")]
                    if int(hexvalue)<=10 and int(hexvalue)>=5:
                        highmannose.append("True")
                    elif int(hexvalue)<5:
                        highmannose.append("False")
                else:
                    highmannose.append("False")
            df["High Mannose"]=highmannose
            
            #all unique glycopeptides (charge agnostic)
            glycopeptide=df[["PEP.StrippedSequence","EG.ModifiedPeptide","Total Glycan Composition","PG.ProteinGroups"]].drop_duplicates()
            #all unique glycoproteins
            glycoprotein=df["PG.ProteinGroups"].drop_duplicates()
            
            num_glycoproteins.append(len(glycoprotein))
            num_glycopeptides.append(len(glycopeptide))
            num_glycoPSMs.append(len(df))
            
            dict_glycoproteins[run]=glycoprotein.reset_index(drop=True)
            dict_glycopeptides[run]=glycopeptide.reset_index(drop=True)
            dict_glycoPSMs[run]=df.reset_index(drop=True)

        resultdf_glyco["Cond_Rep"]=searchoutput["Cond_Rep"].drop_duplicates().reset_index(drop=True)
        resultdf_glyco["glycoproteins"]=num_glycoproteins
        resultdf_glyco["glycopeptides"]=num_glycopeptides
        resultdf_glyco["glycoPSM"]=num_glycoPSMs

        glycoproteins_df=pd.DataFrame()
        glycopeptides_df=pd.DataFrame()
        glycoPSMs_df=pd.DataFrame()
        for key in dict_glycoproteins.keys():
            protein_key=pd.DataFrame({"Cond_Rep":[key]*len(dict_glycoproteins[key]),"PG.ProteinGroups":dict_glycoproteins[key]})
            glycoproteins_df=pd.concat([glycoproteins_df,protein_key]).reset_index(drop=True)
            
            peptide_key=pd.DataFrame({"Cond_Rep":[key]*len(dict_glycopeptides[key])})
            peptide_key_df=pd.concat([peptide_key,dict_glycopeptides[key]],axis=1)
            glycopeptides_df=pd.concat([glycopeptides_df,peptide_key_df]).reset_index(drop=True)

            glycoPSMs_df=pd.concat([glycoPSMs_df,dict_glycoPSMs[key]]).reset_index(drop=True)

        return resultdf_glyco,glycoproteins_df,glycopeptides_df,glycoPSMs_df

    # ====================================== Glyco ID Metrics
    #plot only glycosylated IDs
    @reactive.effect
    def _():
        @render.plot(width=input.glycoIDsplot_width(),height=input.glycoIDsplot_height())
        def glycoIDsplot():
            resultdf_glyco,glycoproteins_df,glycopeptides_df,glycoPSMs_df=glyco_variables()
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
            ax3.set_title("Glyco-PSMs",fontsize=titlefont)

            ax1.set_axisbelow(True)
            ax1.grid(linestyle="--")
            ax2.set_axisbelow(True)
            ax2.grid(linestyle="--")
            ax3.set_axisbelow(True)
            ax3.grid(linestyle="--")

    # ====================================== Venn Diagram
    @render.ui
    def glyco_venn_run1_ui():
        resultdf_glyco,glycoproteins_df,glycopeptides_df,glycoPSMs_df=glyco_variables()
        if input.glyco_venn_conditionorrun()=="condition":
            opts=resultdf_glyco["R.Condition"].drop_duplicates().tolist()
            return ui.input_selectize("glyco_venn_run1_list","Pick first condition to compare",choices=opts)
        if input.glyco_venn_conditionorrun()=="individual":
            opts=resultdf_glyco["Cond_Rep"].tolist()
            return ui.input_selectize("glyco_venn_run1_list","Pick first run to compare",choices=opts)   
    @render.ui
    def glyco_venn_run2_ui():
        resultdf_glyco,glycoproteins_df,glycopeptides_df,glycoPSMs_df=glyco_variables()
        if input.glyco_venn_conditionorrun()=="condition":
            opts=resultdf_glyco["R.Condition"].drop_duplicates().tolist()
            return ui.input_selectize("glyco_venn_run2_list","Pick first condition to compare",choices=opts)
        if input.glyco_venn_conditionorrun()=="individual":
            opts=resultdf_glyco["Cond_Rep"].tolist()
            return ui.input_selectize("glyco_venn_run2_list","Pick first run to compare",choices=opts)
    @render.ui
    def glyco_venn_run3_ui():
        if input.glyco_venn_numcircles()=="3":
            resultdf_glyco,glycoproteins_df,glycopeptides_df,glycoPSMs_df=glyco_variables()
            if input.glyco_venn_conditionorrun()=="condition":
                opts=resultdf_glyco["R.Condition"].drop_duplicates().tolist()
                return ui.input_selectize("glyco_venn_run3_list","Pick first condition to compare",choices=opts)
            if input.glyco_venn_conditionorrun()=="individual":
                opts=resultdf_glyco["Cond_Rep"].tolist()
                return ui.input_selectize("glyco_venn_run3_list","Pick first run to compare",choices=opts)   
    #plot Venn Diagram
    @reactive.effect
    def _():
        @render.plot(width=input.glyco_venn_width(),height=input.glyco_venn_height())
        def glyco_venn_plot():
            resultdf_glyco,glycoproteins_df,glycopeptides_df,glycoPSMs_df=glyco_variables()
            if input.glyco_venn_conditionorrun()=="condition":
                A=glycoPSMs_df[glycoPSMs_df["R.Condition"]==input.glyco_venn_run1_list()][["PG.ProteinGroups","EG.ModifiedPeptide","FG.Charge","PEP.StrippedSequence","Total Glycan Composition"]].drop_duplicates().reset_index(drop=True)
                B=glycoPSMs_df[glycoPSMs_df["R.Condition"]==input.glyco_venn_run2_list()][["PG.ProteinGroups","EG.ModifiedPeptide","FG.Charge","PEP.StrippedSequence","Total Glycan Composition"]].drop_duplicates().reset_index(drop=True)
                if input.glyco_venn_numcircles()=="3":
                    C=glycoPSMs_df[glycoPSMs_df["R.Condition"]==input.glyco_venn_run3_list()][["PG.ProteinGroups","EG.ModifiedPeptide","FG.Charge","PEP.StrippedSequence","Total Glycan Composition"]].drop_duplicates().reset_index(drop=True)
            if input.glyco_venn_conditionorrun()=="individual":
                A=glycoPSMs_df[glycoPSMs_df["Cond_Rep"]==input.glyco_venn_run1_list()][["PG.ProteinGroups","EG.ModifiedPeptide","FG.Charge","PEP.StrippedSequence","Total Glycan Composition"]].drop_duplicates().reset_index(drop=True)
                B=glycoPSMs_df[glycoPSMs_df["Cond_Rep"]==input.glyco_venn_run2_list()][["PG.ProteinGroups","EG.ModifiedPeptide","FG.Charge","PEP.StrippedSequence","Total Glycan Composition"]].drop_duplicates().reset_index(drop=True)
                if input.glyco_venn_numcircles()=="3":
                    C=glycoPSMs_df[glycoPSMs_df["Cond_Rep"]==input.glyco_venn_run3_list()][["PG.ProteinGroups","EG.ModifiedPeptide","FG.Charge","PEP.StrippedSequence","Total Glycan Composition"]].drop_duplicates().reset_index(drop=True)
            
            A["modpep_glycan"]=A["EG.ModifiedPeptide"]+"_"+A["Total Glycan Composition"]
            B["modpep_glycan"]=B["EG.ModifiedPeptide"]+"_"+B["Total Glycan Composition"]

            A["modpep_glycan_charge"]=A["EG.ModifiedPeptide"]+"_"+A["Total Glycan Composition"]+"_"+A["FG.Charge"].astype(str)
            B["modpep_glycan_charge"]=B["EG.ModifiedPeptide"]+"_"+B["Total Glycan Composition"]+"_"+B["FG.Charge"].astype(str)

            if input.glyco_venn_numcircles()=="3":
                C["modpep_glycan"]=C["EG.ModifiedPeptide"]+"_"+C["Total Glycan Composition"]
                C["modpep_glycan_charge"]=C["EG.ModifiedPeptide"]+"_"+C["Total Glycan Composition"]+"_"+C["FG.Charge"].astype(str)

            if input.glyco_venn_plotproperty()=="glycoproteins":
                a=set(A["PG.ProteinGroups"])
                b=set(B["PG.ProteinGroups"])
                if input.glyco_venn_numcircles()=="3":
                    c=set(C["PG.ProteinGroups"])
                titlemod="Glycoproteins"
            if input.glyco_venn_plotproperty()=="glycopeptides":
                a=set(A["modpep_glycan"])
                b=set(B["modpep_glycan"])
                if input.glyco_venn_numcircles()=="3":
                    c=set(C["modpep_glycan"])
                titlemod="Glycopeptides"
            if input.glyco_venn_plotproperty()=="glycoPSMs":
                a=set(A["modpep_glycan_charge"])
                b=set(B["modpep_glycan_charge"])
                if input.glyco_venn_numcircles()=="3":
                    c=set(C["modpep_glycan_charge"])
                titlemod="GlycoPSMs"

            fig,ax=plt.subplots()
            if input.glyco_venn_numcircles()=="2":
                Ab=len(a-b)
                aB=len(b-a)
                AB=len(a&b)
                venn2(subsets=(Ab,aB,AB),set_labels=(input.glyco_venn_run1_list(),input.glyco_venn_run2_list()),set_colors=("tab:blue","tab:orange"),ax=ax)
                venn2_circles(subsets=(Ab,aB,AB),linestyle="dashed",linewidth=0.5)
                plt.title("Venn Diagram for "+titlemod)
            if input.glyco_venn_numcircles()=="3":
                Abc=len(a-b-c)
                aBc=len(b-a-c)
                ABc=len((a&b)-c)
                abC=len(c-a-b)
                AbC=len((a&c)-b)
                aBC=len((b&c)-a)
                ABC=len(a&b&c)
                venn3(subsets=(Abc,aBc,ABc,abC,AbC,aBC,ABC),set_labels=(input.glyco_venn_run1_list(),input.glyco_venn_run2_list(),input.glyco_venn_run3_list()),set_colors=("tab:blue","tab:orange","tab:green"),ax=ax)
                venn3_circles(subsets=(Abc,aBc,ABc,abC,AbC,aBC,ABC),linestyle="dashed",linewidth=0.5)
                plt.title("Venn Diagram for "+titlemod)
    #download table of Venn Diagram intersections
    @reactive.effect
    def _():
        if input.glyco_venn_numcircles()=="2":
            filename=lambda: f"VennList_{input.glyco_venn_run1_list()}_vs_{input.glyco_venn_run2_list()}_{input.glyco_venn_plotproperty()}.csv"
        if input.glyco_venn_numcircles()=="3":
            filename=lambda: f"VennList_A-{input.glyco_venn_run1_list()}_vs_B-{input.glyco_venn_run2_list()}_vs_C-{input.glyco_venn_run3_list()}_{input.glyco_venn_plotproperty()}.csv"
        @render.download(filename=filename)
        def glyco_venn_download():
            resultdf_glyco,glycoproteins_df,glycopeptides_df,glycoPSMs_df=glyco_variables()
            if input.glyco_venn_conditionorrun()=="condition":
                A=glycoPSMs_df[glycoPSMs_df["R.Condition"]==input.glyco_venn_run1_list()][["PG.ProteinGroups","EG.ModifiedPeptide","FG.Charge","PEP.StrippedSequence","Total Glycan Composition"]].drop_duplicates().reset_index(drop=True)
                B=glycoPSMs_df[glycoPSMs_df["R.Condition"]==input.glyco_venn_run2_list()][["PG.ProteinGroups","EG.ModifiedPeptide","FG.Charge","PEP.StrippedSequence","Total Glycan Composition"]].drop_duplicates().reset_index(drop=True)
                if input.glyco_venn_numcircles()=="3":
                    C=glycoPSMs_df[glycoPSMs_df["R.Condition"]==input.glyco_venn_run3_list()][["PG.ProteinGroups","EG.ModifiedPeptide","FG.Charge","PEP.StrippedSequence","Total Glycan Composition"]].drop_duplicates().reset_index(drop=True)
            if input.glyco_venn_conditionorrun()=="individual":
                A=glycoPSMs_df[glycoPSMs_df["Cond_Rep"]==input.glyco_venn_run1_list()][["PG.ProteinGroups","EG.ModifiedPeptide","FG.Charge","PEP.StrippedSequence","Total Glycan Composition"]].drop_duplicates().reset_index(drop=True)
                B=glycoPSMs_df[glycoPSMs_df["Cond_Rep"]==input.glyco_venn_run2_list()][["PG.ProteinGroups","EG.ModifiedPeptide","FG.Charge","PEP.StrippedSequence","Total Glycan Composition"]].drop_duplicates().reset_index(drop=True)
                if input.glyco_venn_numcircles()=="3":
                    C=glycoPSMs_df[glycoPSMs_df["Cond_Rep"]==input.glyco_venn_run3_list()][["PG.ProteinGroups","EG.ModifiedPeptide","FG.Charge","PEP.StrippedSequence","Total Glycan Composition"]].drop_duplicates().reset_index(drop=True)
            
            A["modpep_glycan"]=A["EG.ModifiedPeptide"]+"_"+A["Total Glycan Composition"]
            B["modpep_glycan"]=B["EG.ModifiedPeptide"]+"_"+B["Total Glycan Composition"]

            A["modpep_glycan_charge"]=A["EG.ModifiedPeptide"]+"_"+A["Total Glycan Composition"]+"_"+A["FG.Charge"].astype(str)
            B["modpep_glycan_charge"]=B["EG.ModifiedPeptide"]+"_"+B["Total Glycan Composition"]+"_"+B["FG.Charge"].astype(str)

            if input.glyco_venn_numcircles()=="3":
                C["modpep_glycan"]=C["EG.ModifiedPeptide"]+"_"+C["Total Glycan Composition"]
                C["modpep_glycan_charge"]=C["EG.ModifiedPeptide"]+"_"+C["Total Glycan Composition"]+"_"+C["FG.Charge"].astype(str)

            if input.glyco_venn_plotproperty()=="glycoproteins":
                a=set(A["PG.ProteinGroups"])
                b=set(B["PG.ProteinGroups"])
                if input.glyco_venn_numcircles()=="3":
                    c=set(C["PG.ProteinGroups"])
                titlemod="Glycoproteins"
            if input.glyco_venn_plotproperty()=="glycopeptides":
                a=set(A["modpep_glycan"])
                b=set(B["modpep_glycan"])
                if input.glyco_venn_numcircles()=="3":
                    c=set(C["modpep_glycan"])
                titlemod="Glycopeptides"
            if input.glyco_venn_plotproperty()=="glycoPSMs":
                a=set(A["modpep_glycan_charge"])
                b=set(B["modpep_glycan_charge"])
                if input.glyco_venn_numcircles()=="3":
                    c=set(C["modpep_glycan_charge"])
                titlemod="GlycoPSMs"

            df=pd.DataFrame()
            if input.glyco_venn_numcircles()=="2":
                Ab=list(a-b)
                aB=list(b-a)
                AB=list(a&b)
                df=pd.concat([df,pd.Series(Ab,name=input.glyco_venn_run1_list())],axis=1)
                df=pd.concat([df,pd.Series(aB,name=input.glyco_venn_run2_list())],axis=1)
                df=pd.concat([df,pd.Series(AB,name="Both")],axis=1)
            if input.glyco_venn_numcircles()=="3":
                Abc=list(a-b-c)
                aBc=list(b-a-c)
                ABc=list((a&b)-c)
                abC=list(c-a-b)
                AbC=list((a&c)-b)
                aBC=list((b&c)-a)
                ABC=list(a&b&c)
                df=pd.concat([df,pd.Series(Abc,name="A only")],axis=1)
                df=pd.concat([df,pd.Series(aBc,name="B only")],axis=1)
                df=pd.concat([df,pd.Series(ABc,name="A and B, not C")],axis=1)
                df=pd.concat([df,pd.Series(abC,name="C only")],axis=1)
                df=pd.concat([df,pd.Series(AbC,name="A and C, not B")],axis=1)
                df=pd.concat([df,pd.Series(aBC,name="B and C, not A")],axis=1)
                df=pd.concat([df,pd.Series(ABC,name="ABC")],axis=1)
            with io.BytesIO() as buf:
                df.to_csv(buf,index=False)
                yield buf.getvalue()            

    # ====================================== Glyco ID Tables
    #show data grid for glycoproteins
    @render.data_frame
    def glycoproteins_df_view():
        resultdf_glyco,glycoproteins_df,glycopeptides_df,glycoPSMs_df=glyco_variables()
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
        resultdf_glyco,glycoproteins_df,glycopeptides_df,glycoPSMs_df=glyco_variables()
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
        resultdf_glyco,glycoproteins_df,glycopeptides_df,glycoPSMs_df=glyco_variables()
        return render.DataGrid(glycoPSMs_df,editable=False,height="600px")
    #download shown data grid for glyco PSMs
    @render.download(filename=lambda: f"glycoPSMs_{input.searchreport()[0]['name']}.csv")
    def glycoPSMs_download():
        glycoPSMs_table=glycoPSMs_df_view.data_view()
        with io.BytesIO() as buf:
            glycoPSMs_table.to_csv(buf,index=False)
            yield buf.getvalue()

    # ====================================== Glycan Tracker
    #generate selectize list of detected glyco mods
    @render.ui
    def glycomodlist_ui():
        #glycoproteins_df,glycopeptides_df,glycoPSMs_df=glyco_dataframes()
        resultdf_glyco,glycoproteins_df,glycopeptides_df,glycoPSMs_df=glyco_variables()

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
    @render.ui
    def high_mannose_ui():
        if input.found_glycomods()=="Hex":
            return ui.input_switch("high_mannose","Show only high mannose?")
    #plot ID bar graph for selected glyco mod, option to show % instead of counts
    @reactive.effect
    def _():
        @render.plot(width=input.glycomodIDsplot_width(),height=input.glycomodIDsplot_height())
        def glycomod_IDs():
            resultdf_glyco,glycoproteins_df,glycopeptides_df,glycoPSMs_df=glyco_variables()
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
                if picked_mod!="Hex":
                    num_glycoproteins_mod.append(len(glycoPSMs_df[(glycoPSMs_df["Cond_Rep"]==run)&(glycoPSMs_df["Total Glycan Composition"].str.contains(picked_mod))]["PG.ProteinGroups"].drop_duplicates()))
                    num_glycopeptides_mod.append(len(glycoPSMs_df[(glycoPSMs_df["Cond_Rep"]==run)&(glycoPSMs_df["Total Glycan Composition"].str.contains(picked_mod))]["EG.ModifiedPeptide"].drop_duplicates()))
                    num_glycoPSMs_mod.append(len(glycoPSMs_df[(glycoPSMs_df["Cond_Rep"]==run)&(glycoPSMs_df["Total Glycan Composition"].str.contains(picked_mod))]))
                else:
                    if input.high_mannose()==True:
                        num_glycoproteins_mod.append(len(glycoPSMs_df[(glycoPSMs_df["Cond_Rep"]==run)&(glycoPSMs_df["Total Glycan Composition"].str.contains(picked_mod))&(glycoPSMs_df["High Mannose"]=="True")]["PG.ProteinGroups"].drop_duplicates()))
                        num_glycopeptides_mod.append(len(glycoPSMs_df[(glycoPSMs_df["Cond_Rep"]==run)&(glycoPSMs_df["Total Glycan Composition"].str.contains(picked_mod))&(glycoPSMs_df["High Mannose"]=="True")]["EG.ModifiedPeptide"].drop_duplicates()))
                        num_glycoPSMs_mod.append(len(glycoPSMs_df[(glycoPSMs_df["Cond_Rep"]==run)&(glycoPSMs_df["Total Glycan Composition"].str.contains(picked_mod))&(glycoPSMs_df["High Mannose"]=="True")]))
                    else:
                        num_glycoproteins_mod.append(len(glycoPSMs_df[(glycoPSMs_df["Cond_Rep"]==run)&(glycoPSMs_df["Total Glycan Composition"].str.contains(picked_mod))]["PG.ProteinGroups"].drop_duplicates()))
                        num_glycopeptides_mod.append(len(glycoPSMs_df[(glycoPSMs_df["Cond_Rep"]==run)&(glycoPSMs_df["Total Glycan Composition"].str.contains(picked_mod))]["EG.ModifiedPeptide"].drop_duplicates()))
                        num_glycoPSMs_mod.append(len(glycoPSMs_df[(glycoPSMs_df["Cond_Rep"]==run)&(glycoPSMs_df["Total Glycan Composition"].str.contains(picked_mod))]))

            resultdf_glycomod["Cond_Rep"]=glycoPSMs_df["Cond_Rep"].drop_duplicates().reset_index(drop=True)
            resultdf_glycomod["glycoproteins"]=num_glycoproteins_mod
            resultdf_glycomod["glycopeptides"]=num_glycopeptides_mod
            resultdf_glycomod["glycoPSM"]=num_glycoPSMs_mod

            if input.counts_vs_enrich()=="counts":
                plottingdf=resultdf_glycomod
                ylabel="Counts"
            if input.counts_vs_enrich()=="percent":
                resultdf_glyco_enrich=round(resultdf_glycomod.drop(columns=["Cond_Rep"])/resultdf_glyco.drop(columns=["Cond_Rep"])*100,1)
                resultdf_glyco_enrich["Cond_Rep"]=glycoPSMs_df["Cond_Rep"].drop_duplicates().reset_index(drop=True)
                plottingdf=resultdf_glyco_enrich
                ylabel="% of IDs"

            fig,ax=plt.subplots(ncols=3,sharex=True)
            fig.set_tight_layout(True)
            ax1=ax[0]
            ax2=ax[1]
            ax3=ax[2]

            plottingdf.plot.bar(ax=ax1,x="Cond_Rep",y="glycoproteins",legend=False,width=0.8,color=color,edgecolor="k")
            ax1.bar_label(ax1.containers[0],label_type="edge",rotation=90,padding=5,fontsize=labelfont)
            ax1.set_ylim(top=max(plottingdf["glycoproteins"].tolist())+y_padding*max(plottingdf["glycoproteins"].tolist()))
            ax1.set_ylabel(ylabel,fontsize=axisfont)
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
            ax3.set_title("Glyco-PSMs",fontsize=titlefont)

            ax1.set_axisbelow(True)
            ax1.grid(linestyle="--")
            ax2.set_axisbelow(True)
            ax2.grid(linestyle="--")
            ax3.set_axisbelow(True)
            ax3.grid(linestyle="--")

    # ====================================== Peptide Tracker
    #generate selectize list of stripped peptide sequences
    @render.ui
    def glyco_peplist():
        resultdf_glyco,glycoproteins_df,glycopeptides_df,glycoPSMs_df=glyco_variables()
        peplist=glycoPSMs_df["PEP.StrippedSequence"].drop_duplicates().sort_values().reset_index(drop=True).tolist()
        pep_dict=dict()
        for pep in peplist:
            pep_dict[pep]=pep
        return ui.input_selectize("glyco_peplist_pick","Pick stripped peptide sequence:",choices=pep_dict)
    #show glycoPSMs for selected stripped peptide sequence 
    @render.data_frame
    def selected_glyco_peplist():
        resultdf_glyco,glycoproteins_df,glycopeptides_df,glycoPSMs_df=glyco_variables()
        selectedpep=input.glyco_peplist_pick()
        selectedpep_df=glycoPSMs_df[glycoPSMs_df["PEP.StrippedSequence"]==selectedpep]
        return render.DataGrid(selectedpep_df,editable=False,height="600px")
    #download shown table of glycoPSMs for selected stripped peptide sequence
    @render.download(filename=lambda: f"glycoPSMs_{input.glyco_peplist_pick()}.csv")
    def selected_glyco_download():
        resultdf_glyco,glycoproteins_df,glycopeptides_df,glycoPSMs_df=glyco_variables()
        glycopep_table=selected_glyco_peplist.data_view()
        with io.BytesIO() as buf:
            glycopep_table.to_csv(buf,index=False)
            yield buf.getvalue()

    # ====================================== Precursor Scatterplot
    @render.ui
    def glycoscatter_ui():
        searchoutput=metadata_update()
        opts=searchoutput["Cond_Rep"].drop_duplicates().tolist()
        return ui.input_selectize("glycoscatter_pick","Pick run:",choices=opts)
    #scatterplot like the charge/PTM scatter for glycosylated precursors
    @reactive.effect
    def _():
        @render.plot(width=input.glycoscatter_width(),height=input.glycoscatter_height())
        def glycoscatter():
            searchoutput=metadata_update()

            if input.software()=="fragpipe_glyco":
                searchoutput_nonglyco=searchoutput[(searchoutput["Glycan q-value"].isnull()==True)&(searchoutput["Cond_Rep"]==input.glycoscatter_pick())]
                searchoutput_glyco=searchoutput[(searchoutput["Glycan q-value"].isnull()==False)&(searchoutput["Cond_Rep"]==input.glycoscatter_pick())]
            if input.software()=="glycoscape":
                searchoutput_nonglyco=searchoutput[(searchoutput["Total Glycan Composition"].isnull()==True)&(searchoutput["Cond_Rep"]==input.glycoscatter_pick())]
                searchoutput_glyco=searchoutput[(searchoutput["Total Glycan Composition"].isnull()==False)&(searchoutput["Cond_Rep"]==input.glycoscatter_pick())]

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

#endregion

# ============================================================================= MOMA
#region
    #choose whether to import data from individual file names or from a directory
    @render.ui
    def moma_rawfile_input_ui():
        if input.moma_file_or_folder()=="individual":
            return ui.input_text_area("moma_rawfile_input","Paste the path for each .d file you want to upload (note: do not leave whitespace at the end):",width="1500px",autoresize=True,placeholder="ex - C:\\Users\\Data\\K562_500ng_1_Slot1-49_1_3838.d")
        if input.moma_file_or_folder()=="directory":
            return ui.input_text_area("moma_rawfile_input","Paste the path for the directory containing the raw files to upload (note: do not leave whitespace at the end):",width="1500px",autoresize=True,placeholder="ex - C:\\Users\\Data")

    #list to choose raw data file to plot EIM for
    @render.ui
    def moma_rawfile_buttons_ui():
        if input.moma_file_or_folder()=="individual":
            filelist=list(input.moma_rawfile_input().split("\n"))
            samplenames=[]
            for run in filelist:
                samplenames.append(run.split("\\")[-1])
        if input.moma_file_or_folder()=="directory":
            try:
                os.chdir(input.moma_rawfile_input())
                cwd=os.getcwd()
                filelist=[]
                for file in os.listdir():
                    if ".d" in file:
                        filelist.append(cwd+"\\"+file)
                samplenames=[]
                for run in filelist:
                    samplenames.append(run.split("\\")[-1])
            except:
                samplenames=[""]
        return ui.input_radio_buttons("moma_rawfile_buttons_pick","Pick raw file for EIM:",choices=samplenames,width="100%")

    #render ui call for dropdown calling Cond_Rep column
    @render.ui
    def moma_cond_rep_list():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
        opts=resultdf["Cond_Rep"].tolist()
        return ui.input_radio_buttons("moma_cond_rep","Pick run from search file:",choices=opts)
    
    #store imported raw file as a reactive value upon button press
    @reactive.calc
    @reactive.event(input.moma_load_rawfile)
    def rawfile_import():
        if input.moma_file_or_folder()=="individual":
            run=input.moma_rawfile_input()
        if input.moma_file_or_folder()=="directory":
            directory=input.moma_rawfile_input()
            selectedrun=input.moma_rawfile_buttons_pick()
            run=directory+"\\"+selectedrun
        rawfile=atb.TimsTOF(run)
        return rawfile

    #text popup for when the input file is loaded
    @render.text
    def file_uploaded():
        rawfile=rawfile_import()
        if rawfile is None:
            return ""
        else:
            return "Raw File Loaded"

    #table of MOMA events from search file
    @render.data_frame
    def moma_events():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
        mztolerance=input.moma_mztolerance()
        rttolerance=input.moma_rttolerance()
        imtolerance=input.moma_imtolerance()
        sample=input.moma_cond_rep()

        columns=["EG.ModifiedPeptide","FG.Charge","EG.IonMobility","EG.ApexRT","FG.PrecMz"]
        df=searchoutput[searchoutput["Cond_Rep"]==sample][["EG.ModifiedPeptide","FG.Charge","EG.IonMobility","EG.ApexRT","FG.PrecMz"]].sort_values(["EG.ApexRT"]).reset_index(drop=True)
        coelutingpeptides=pd.DataFrame(columns=columns)
        for i in range(len(df)):
            if i+1 not in range(len(df)):
                break
            #rtpercentdiff=(abs(df["EG.ApexRT"][i]-df["EG.ApexRT"][i+1])/df["EG.ApexRT"][i])*100
            rtdiff=abs(df["EG.ApexRT"][i]-df["EG.ApexRT"][i+1])
            mzdiff=abs(df["FG.PrecMz"][i]-df["FG.PrecMz"][i+1])
            imdiff=abs(df["EG.IonMobility"][i]-df["EG.IonMobility"][i+1])
            if rtdiff <= rttolerance and mzdiff <= mztolerance and imdiff >= imtolerance:
                coelutingpeptides.loc[len(coelutingpeptides)]=df.iloc[i].tolist()
                coelutingpeptides.loc[len(coelutingpeptides)]=df.iloc[i+1].tolist()

        #adding a column for a rough group number for each group of peptides detected
        for i in range(len(coelutingpeptides)):
            if i+1 not in range(len(coelutingpeptides)):
                break
            #rtpercentdiff=(abs(coelutingpeptides["EG.ApexRT"][i]-coelutingpeptides["EG.ApexRT"][i+1])/coelutingpeptides["EG.ApexRT"][i])*100
            rtdiff=abs(coelutingpeptides["EG.ApexRT"][i]-coelutingpeptides["EG.ApexRT"][i+1])
            mzdiff=abs(coelutingpeptides["FG.PrecMz"][i]-coelutingpeptides["FG.PrecMz"][i+1])
            imdiff=abs(coelutingpeptides["EG.IonMobility"][i]-coelutingpeptides["EG.IonMobility"][i+1])
            if rtdiff <= rttolerance and mzdiff <= mztolerance and imdiff >= imtolerance:
                coelutingpeptides.loc[coelutingpeptides.index[i],"Group"]=i
        coelutingpeptides=coelutingpeptides[["Group","EG.ModifiedPeptide","FG.Charge","FG.PrecMz","EG.ApexRT","EG.IonMobility"]]

        return render.DataGrid(coelutingpeptides,editable=False)
    
    @render.plot(width=600,height=600)
    def moma_eim():
        rawfile=rawfile_import()
        try:
            mz=float(input.moma_mz())
            rt=float(input.moma_rt())
            mz_window=input.moma_mztolerance()
            rt_window=input.moma_rttolerance()

            low_mz=mz-mz_window
            high_mz=mz+mz_window
            low_rt=(rt-rt_window)*60
            #(rt-(rt*(rt_window/100)))*60
            high_rt=(rt+rt_window)*60
            #(rt+(rt*(rt_window/100)))*60

            eim_df=rawfile[low_rt: high_rt,:,0,low_mz: high_mz].sort_values("mobility_values")

            fig,ax=plt.subplots()
            ax.plot(eim_df["mobility_values"],eim_df["intensity_values"])
            ax.set_xlabel("Ion Mobility ($1/K_{0}$)")
            ax.set_ylabel("Intensity")
            ax.xaxis.set_minor_locator(MultipleLocator(0.025))
            ax.set_title("EIM")
        except:
            fig,ax=plt.subplots()

    @render.download(filename=lambda: f"{input.moma_cond_rep()}_MOMA_events.csv")
    def momatable_download():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
        mztolerance=input.moma_mztolerance()
        rttolerance=input.moma_rttolerance()
        imtolerance=input.moma_imtolerance()
        sample=input.moma_cond_rep()

        columns=["EG.ModifiedPeptide","FG.Charge","EG.IonMobility","EG.ApexRT","FG.PrecMz"]
        df=searchoutput[searchoutput["Cond_Rep"]==sample][["EG.ModifiedPeptide","FG.Charge","EG.IonMobility","EG.ApexRT","FG.PrecMz"]].sort_values(["EG.ApexRT"]).reset_index(drop=True)
        coelutingpeptides=pd.DataFrame(columns=columns)
        for i in range(len(df)):
            if i+1 not in range(len(df)):
                break
            #rtpercentdiff=(abs(df["EG.ApexRT"][i]-df["EG.ApexRT"][i+1])/df["EG.ApexRT"][i])*100
            rtdiff=abs(df["EG.ApexRT"][i]-df["EG.ApexRT"][i+1])
            mzdiff=abs(df["FG.PrecMz"][i]-df["FG.PrecMz"][i+1])
            imdiff=abs(df["EG.IonMobility"][i]-df["EG.IonMobility"][i+1])
            if rtdiff <= rttolerance and mzdiff <= mztolerance and imdiff >= imtolerance:
                coelutingpeptides.loc[len(coelutingpeptides)]=df.iloc[i].tolist()
                coelutingpeptides.loc[len(coelutingpeptides)]=df.iloc[i+1].tolist()

        #adding a column for a rough group number for each group of peptides detected
        for i in range(len(coelutingpeptides)):
            if i+1 not in range(len(coelutingpeptides)):
                break
            #rtpercentdiff=(abs(coelutingpeptides["EG.ApexRT"][i]-coelutingpeptides["EG.ApexRT"][i+1])/coelutingpeptides["EG.ApexRT"][i])*100
            rtdiff=abs(coelutingpeptides["EG.ApexRT"][i]-coelutingpeptides["EG.ApexRT"][i+1])
            mzdiff=abs(coelutingpeptides["FG.PrecMz"][i]-coelutingpeptides["FG.PrecMz"][i+1])
            imdiff=abs(coelutingpeptides["EG.IonMobility"][i]-coelutingpeptides["EG.IonMobility"][i+1])
            if rtdiff <= rttolerance and mzdiff <= mztolerance and imdiff >= imtolerance:
                coelutingpeptides.loc[coelutingpeptides.index[i],"Group"]=i
        coelutingpeptides=coelutingpeptides[["Group","EG.ModifiedPeptide","FG.Charge","FG.PrecMz","EG.ApexRT","EG.IonMobility"]]
        with io.BytesIO() as buf:
            coelutingpeptides.to_csv(buf,index=False)
            yield buf.getvalue()

    @render.download(filename=lambda: f"{input.moma_rawfile_buttons_pick()}_MOMA_precursors.csv")
    def precursortable_download():
        rawfile=rawfile_import()
        mz=float(input.moma_mz())
        rt=float(input.moma_rt())
        mz_window=input.moma_mztolerance()
        rt_window=input.moma_rttolerance()

        low_mz=mz-mz_window
        high_mz=mz+mz_window
        low_rt=(rt-rt_window)*60
        #(rt-(rt*(rt_window/100)))*60
        high_rt=(rt+rt_window)*60
        #(rt+(rt*(rt_window/100)))*60

        eim_df=rawfile[low_rt: high_rt,:,0,low_mz: high_mz].sort_values("mobility_values")
        with io.BytesIO() as buf:
            eim_df.to_csv(buf,index=False)
            yield buf.getvalue()

#endregion

# ============================================================================= De Novo
#region
    # ====================================== Secondary File Import
    #region
    #import search report file
    @reactive.calc
    def inputfile_secondary():
        if input.searchreport_secondary() is None:
            return pd.DataFrame()
        if ".tsv" in input.searchreport_secondary()[0]["name"]:
            if len(input.searchreport_secondary())>1:
                searchoutput=pd.DataFrame()
                for i in range(len(input.searchreport_secondary())):
                    run=pd.read_csv(input.searchreport_secondary()[i]["datapath"],sep="\t")
                    searchoutput=pd.concat([searchoutput,run])
            else:
                searchoutput=pd.read_csv(input.searchreport_secondary()[0]["datapath"],sep="\t")
            if input.software_secondary()=="diann":
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
                                            "Predicted.iIM","PG.Normalised","PTM.Informative","PTM.Specific","PTM.Localising",
                                            "PTM.Q.Value","PTM.Site.Confidence","Lib.PTM.Site.Confidence"],inplace=True,errors='ignore')
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
            if input.software_secondary()=="fragpipe":
                searchoutput.rename(columns={"Spectrum File":"R.FileName"},inplace=True)
                searchoutput.insert(1,"R.Condition","")
                searchoutput.insert(2,"R.Replicate","")
                
                searchoutput["FG.CalibratedMassAccuracy (PPM)"]=(searchoutput["Delta Mass"]/searchoutput["Calculated M/Z"])*10E6

                searchoutput.drop(columns=["Spectrum","Extended Peptide","Prev AA","Next AA","Peptide Length",
                                        "Observed Mass","Calibrated Observed Mass","Calibrated Observed M/Z",
                                        "Calculated Peptide Mass","Calculated M/Z","Delta Mass",
                                        "Expectation","Hyperscore","Nextscore",
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
                    "43":"Acetyl (Protein N-term)",
                    "111":""},regex=True)

                peps=searchoutput["PEP.StrippedSequence"].tolist()
                modpeps=searchoutput["EG.ModifiedPeptide"].tolist()
                for i in range(len(peps)):
                    if type(modpeps[i])!=str:
                        modpeps[i]=peps[i]
                    else:
                        modpeps[i]=modpeps[i]
                searchoutput["EG.ModifiedPeptide"]=modpeps
            if input.software_secondary()=="fragpipe_glyco":
                #if the Spectrum File column is just a single value, get the file names from the Spectrum column
                if searchoutput["Spectrum"][0].split(".")[0] not in searchoutput["Spectrum File"][0]:
                    fragger_filelist=searchoutput["Spectrum"].str.split(".",expand=True).drop(columns=[1,2,3]).drop_duplicates().reset_index(drop=True)
                    fragger_filelist.rename(columns={0:"R.FileName"},inplace=True)

                    filenamelist=[]
                    for run in fragger_filelist["R.FileName"]:
                        fileindex=fragger_filelist[fragger_filelist["R.FileName"]==run].index.values[0]
                        filenamelist.append([fragger_filelist["R.FileName"][fileindex]]*len(searchoutput[searchoutput["Spectrum"].str.contains(run)]))

                    searchoutput.insert(0,"R.FileName",list(itertools.chain(*filenamelist)))
                    searchoutput.drop(columns=["Spectrum File"],inplace=True)

                else:
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
        
        #for BPS input
        if ".zip" in input.searchreport_secondary()[0]["name"]:
            if input.software_secondary()=="bps_timsrescore":
                searchoutput=pd.DataFrame()

                bpszip=ZipFile(input.searchreport_secondary()[0]["datapath"])
                bpszip.extractall()
                metadata_bps=pd.read_csv("metadata.csv")
                runlist=metadata_bps["processing_run_uuid"].tolist()
                cwd=os.getcwd()+"\\processing-run"
                os.chdir(cwd)

                peptide_dict=dict()
                samplename_list=[]
                for run in runlist:
                    #change working dir to next processing run subfolder
                    os.chdir(cwd+"\\"+run)
                    #read files from each processing run subfolder, I think only ones that are neeed are pgfdr.peptide and summary-results
                    #candidates=pd.read_parquet("candidates.candidates.parquet")
                    #timsrescorer=pd.read_parquet("timsrescorer.psm.parquet")
                    pgfdr_peptide=pd.read_parquet("pgfdr.peptide.parquet")
                    #pgfdr_protein=pd.read_parquet("pgfdr.protein.parquet")
                    #summary_results=pd.read_parquet("summary-results.results.parquet")
                    #samplename=summary_results["sample_name"][0]
                    #samplename_list.append(samplename)
                    
                    peptide_dict[run]=pgfdr_peptide

                #filter, rename/remove columns, and generate ProteinGroups and ProteinNames columns from protein_list column
                for key in peptide_dict.keys():
                    df=peptide_dict[key][peptide_dict[key]["protein_list"].str.contains("Reverse")==False].reset_index(drop=True)
                    df=df.rename(columns={"sample_name":"R.FileName",
                                    "stripped_peptide":"PEP.StrippedSequence",
                                    "precursor_mz":"FG.PrecMz",
                                    "rt":"EG.ApexRT",
                                    "charge":"FG.Charge",
                                    "ook0":"EG.IonMobility",
                                    "ppm_error":"FG.CalibratedMassAccuracy (PPM)"})

                    proteingroups=[]
                    proteinnames=[]
                    proteinlist_column=df["protein_list"].tolist()
                    for item in proteinlist_column:
                        if item.count(";")==0:
                            templist=item.split("|")
                            proteingroups.append(templist[1])
                            proteinnames.append(templist[2])
                        else:
                            proteingroups_torejoin=[]
                            proteinnames_torejoin=[]
                            for entry in item.split(";"):
                                templist=entry.split("|")
                                proteingroups_torejoin.append(templist[1])
                                proteinnames_torejoin.append(templist[2])
                            proteingroups.append(";".join(proteingroups_torejoin))
                            proteinnames.append(";".join(proteinnames_torejoin))
                    df["PG.ProteinGroups"]=proteingroups
                    df["PG.ProteinNames"]=proteinnames
                    
                    #adding a q-value filter before dropping the column
                    df=df[df["global_peptide_qvalue"]<=0.01]

                    df=df.drop(columns=["index","processing_run_uuid","ms2_id","candidate_id","protein_group_parent_id",
                                    "protein_group_name","leading_aa","trailing_aa","mokapot_psm_score","mokapot_psm_qvalue",
                                    "mokapot_psm_pep","mokapot_peptide_qvalue","mokapot_peptide_pep","global_peptide_score",
                                    "x_corr_score","delta_cn_score","precursor_mh","calc_mh","protein_list","is_contaminant",
                                    "is_target","number_matched_ions","global_peptide_qvalue"],errors='ignore')
                    
                    searchoutput=pd.concat([searchoutput,df],ignore_index=True)

                #rename ptms 
                searchoutput=searchoutput.reset_index(drop=True)
                searchoutput["ptms"]=searchoutput["ptms"].astype(str)
                searchoutput["ptms"]=searchoutput["ptms"].replace({
                        "42.010565":"Acetyl (Protein N-term)",
                        "57.021464":"Carbamidomethyl (C)",
                        "79.966331":"Phospho (STY)",
                        "15.994915":"Oxidation (M)"},regex=True)

                searchoutput["ptm_locations"]=searchoutput["ptm_locations"].astype(str)
                searchoutput["ptm_locations"]=searchoutput["ptm_locations"].str.replace("[]","-1").str.replace("[","").str.replace("]","")

                #build and add the EG.ModifiedPeptide column
                modifiedpeptides=[]
                for i,entry in enumerate(searchoutput["ptm_locations"]):
                    if entry=="-1":
                        modifiedpeptides.append(searchoutput["PEP.StrippedSequence"][i])
                    else:
                        str_to_list=list(searchoutput["PEP.StrippedSequence"][i])
                        if len(searchoutput["ptm_locations"][i])==1:
                            mod_loc=int(searchoutput["ptm_locations"][i])+1
                            mod_add=searchoutput["ptms"][i]
                            str_to_list.insert(mod_loc,mod_add)
                            modifiedpeptides.append("".join(str_to_list))
                        #if theres >1 ptm, we need to reformat some strings so we can insert them in the sequence
                        else:
                            ptmlocs=searchoutput["ptm_locations"][i].strip().split(" ")
                            ptms=searchoutput["ptms"][i].replace("[","").replace("]","").replace(") ","),").split(",")
                            ptms_for_loop=[]
                            for ele in ptms:
                                ptms_for_loop.append("["+ele+"]")
                            for j,loc in enumerate(ptmlocs):
                                mod_loc=int(loc)+j+1
                                mod_add=ptms_for_loop[j]
                                str_to_list.insert(mod_loc,mod_add)
                            modifiedpeptides.append("".join(str_to_list))
                searchoutput["EG.ModifiedPeptide"]=modifiedpeptides
                searchoutput=searchoutput.drop(columns=["ptms","ptm_locations"])

                searchoutput.insert(1,"R.Condition","")
                searchoutput.insert(2,"R.Replicate","")
                
                #change the cwd back to the code file since we changed it to the uploaded file 
                os.chdir(os.path.dirname(os.path.realpath(__file__)))
            if input.software_secondary()=="bps_timsdiann":
                searchoutput=pd.DataFrame()

                bpszip=ZipFile(input.searchreport_secondary()[0]["datapath"])
                bpszip.extractall()
                metadata_bps=pd.read_csv("metadata.csv")
                runlist=metadata_bps["processing_run_uuid"].tolist()
                cwd=os.getcwd()+"\\processing-run"
                os.chdir(cwd)

                for run in runlist:
                    os.chdir(cwd)
                    os.chdir(os.getcwd()+"\\"+run)
                    bps_resultzip=ZipFile("tims-diann.result.zip")
                    bps_resultzip.extractall()
                    results=pd.read_csv("results.tsv",sep="\t")
                    searchoutput=pd.concat([searchoutput,results])

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
                                        "Precursor.Calibrated.Mz","Fragment.Info","Fragment.Calibrated.Mz","Lib.1/K0",
                                        "Precursor.Normalised"],inplace=True,errors='ignore')

                searchoutput.rename(columns={"File.Name":"R.FileName",
                                            "Protein.Group":"PG.ProteinGroups",
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

                searchoutput.insert(1,"R.Condition","")
                searchoutput.insert(2,"R.Replicate","")
                
                #change the cwd back to the code file since we changed it to the uploaded file 
                os.chdir(os.path.dirname(os.path.realpath(__file__)))
            if input.software_secondary()=="bps_denovo":
                denovo_score=65.0

                searchoutput=pd.DataFrame()

                bpszip=ZipFile(input.searchreport()[0]["datapath"])
                bpszip.extractall()
                metadata_bps=pd.read_csv("metadata.csv")
                runlist=metadata_bps["processing_run_uuid"].tolist()
                cwd=os.getcwd()+"\\processing-run"
                os.chdir(cwd)

                peptide_dict=dict()
                protein_dict=dict()
                for run in runlist:
                    #change working dir to next processing run subfolder
                    os.chdir(cwd+"\\"+run)

                    peptide_dict[run]=pd.read_parquet("novor-fasta-mapping-results.peptide.parquet")
                    protein_dict[run]=pd.read_parquet("novor-fasta-mapping-results.protein.parquet")

                for key in peptide_dict.keys():
                    peptideparquet=peptide_dict[key]
                    proteinparquet=protein_dict[key]

                    #filter parquet file
                    peptideparquet=peptideparquet[(peptideparquet["denovo_score"]>=denovo_score)&(peptideparquet["rank"]==1)].reset_index(drop=True)

                    #rename columns
                    peptideparquet.rename(columns={"sample_name":"R.FileName",
                                                "stripped_peptide":"PEP.StrippedSequence",
                                                "precursor_mz":"FG.PrecMz",
                                                "charge":"FG.Charge",
                                                "ppm_error":"FG.CalibratedMassAccuracy (PPM)",
                                                "rt":"EG.ApexRT",
                                                "ook0":"EG.IonMobility",
                                                "precursor_intensity":"FG.MS2Quantity"
                                                },inplace=True)

                    #drop columns
                    peptideparquet.drop(columns=["index","processing_run_id","ms2_id","rank","leading_aa","trailing_aa","precursor_mh",
                                                "calc_mh","denovo_tag_length","found_in_dbsearch","denovo_matches_db",
                                                "protein_group_parent_loc","protein_group_parent_list_loc","protein_group_parent_list_id"
                                                ],inplace=True,errors='ignore')
                    #fill NaN in the protein group column with -1
                    peptideparquet["protein_group_parent_id"]=peptideparquet["protein_group_parent_id"].fillna(-1)

                    #pull protein and gene info from protein parquet file and add to df 
                    protein_name=[]
                    protein_accession=[]
                    gene_id=[]
                    uncategorized_placeholder="uncat"

                    for i in range(len(peptideparquet["protein_group_parent_id"])):
                        if peptideparquet["protein_group_parent_id"][i]==-1:
                            protein_name.append(uncategorized_placeholder)
                            protein_accession.append(uncategorized_placeholder)
                            gene_id.append(uncategorized_placeholder)
                        else:
                            protein_name.append(proteinparquet["protein_name"].iloc[int(peptideparquet["protein_group_parent_id"][i])])
                            protein_accession.append(proteinparquet["protein_accession"].iloc[int(peptideparquet["protein_group_parent_id"][i])])
                            gene_id.append(proteinparquet["gene_id"].iloc[int(peptideparquet["protein_group_parent_id"][i])])

                    peptideparquet["PG.ProteinGroups"]=protein_name
                    peptideparquet["PG.ProteinAccessions"]=protein_accession
                    peptideparquet["PG.Genes"]=gene_id
                    peptideparquet=peptideparquet.drop(columns=["protein_group_parent_id"])

                    searchoutput=pd.concat([searchoutput,peptideparquet],ignore_index=True)

                #rename PTMs
                searchoutput["ptms"]=searchoutput["ptms"].astype(str)
                searchoutput["ptms"]=searchoutput["ptms"].replace({"57.0215":"Carbamidomethyl (C)",
                                                                    "15.9949":"Oxidation (M)",
                                                                    "15.994915":"Oxidation (M)",
                                                                    "79.966331":"Phospho (STY)",
                                                                    "0.984":"Deamidation (NQ)",
                                                                    },regex=True)
                searchoutput["ptm_locations"]=searchoutput["ptm_locations"].astype(str)
                searchoutput["ptm_locations"]=searchoutput["ptm_locations"].str.replace("[]","[-1]").str.replace("[","").str.replace("]","")

                #build and add the EG.ModifiedPeptide column
                modifiedpeptides=[]
                for i,entry in enumerate(searchoutput["ptm_locations"]):
                    if entry=="-1":
                        modifiedpeptides.append(searchoutput["PEP.StrippedSequence"][i])
                    else:
                        str_to_list=list(searchoutput["PEP.StrippedSequence"][i])
                        if len(searchoutput["ptm_locations"][i])==1:
                            mod_loc=int(searchoutput["ptm_locations"][i])+1
                            mod_add=searchoutput["ptms"][i]
                            str_to_list.insert(mod_loc,mod_add)
                            modifiedpeptides.append("".join(str_to_list))
                        #if theres >1 ptm, we need to reformat some strings so we can insert them in the sequence
                        else:
                            ptmlocs=searchoutput["ptm_locations"][i].strip().split(" ")
                            ptms=searchoutput["ptms"][i].replace("[","").replace("]","").replace(") ","),").split(",")
                            for ele in ptmlocs:
                                if ele=="":
                                    ptmlocs.remove(ele)
                            ptms_for_loop=[]
                            for ele in ptms:
                                ptms_for_loop.append("["+ele+"]")
                            for j,loc in enumerate(ptmlocs):
                                mod_loc=int(loc)+j+1
                                mod_add=ptms_for_loop[j]
                                str_to_list.insert(mod_loc,mod_add)
                            modifiedpeptides.append("".join(str_to_list))
                searchoutput["EG.ModifiedPeptide"]=modifiedpeptides
                searchoutput=searchoutput.drop(columns=["ptms","ptm_locations"])

                searchoutput.insert(1,"R.Condition","")
                searchoutput.insert(2,"R.Replicate","")

                #change the cwd back to the code file since we changed it to the uploaded file 
                os.chdir(os.path.dirname(os.path.realpath(__file__)))
        
        #for DIA-NN 2.0 input
        if ".parquet" in input.searchreport_secondary()[0]["name"]:
            if len(input.searchreport_secondary())>1:
                searchoutput=pd.DataFrame()
                for i in range(len(input.searchreport_secondary())):
                    run=pd.read_parquet(input.searchreport_secondary()[i]["datapath"])
                    searchoutput=pd.concat([searchoutput,run])
            else:
                searchoutput=pd.read_parquet(input.searchreport_secondary()[0]["datapath"])
            if input.software()=="diann2.0":
                searchoutput.rename(columns={"Run":"R.FileName"},inplace=True)
                searchoutput.insert(1,"R.Condition","")
                searchoutput.insert(2,"R.Replicate","")
                searchoutput["EG.PeakWidth"]=searchoutput["RT.Stop"]-searchoutput["RT.Start"]

                searchoutput.rename(columns={"Modified.Sequence":"EG.ModifiedPeptide",
                                            "Stripped.Sequence":"PEP.StrippedSequence",
                                            "Precursor.Charge":"FG.Charge",
                                            "Precursor.Mz":"FG.PrecMz",
                                            "Protein.Group":"PG.ProteinGroups",
                                            "Protein.Names":"PG.ProteinNames",
                                            "Genes":"PG.Genes",
                                            "RT":"EG.ApexRT",
                                            "IM":"EG.IonMobility",
                                            "Precursor.Quantity":"FG.MS2Quantity",
                                            },inplace=True)

                searchoutput.drop(columns=["Run.Index","Channel","Precursor.Id","Precursor.Lib.Index","Decoy",
                                        "Proteotypic","Protein.Ids","iRT","Predicted.RT","Predicted.iRT",
                                        "iIM","Predicted.IM","Predicted.iIM","Precursor.Normalised",
                                        "Ms1.Area","Ms1.Normalised","Ms1.Apex.Area","Ms1.Apex.Mz.Delta",
                                        "Normalisation.Factor","Quantity.Quality","Empirical.Quality",
                                        "Normalisation.Noise","Ms1.Profile.Corr","Evidence","Mass.Evidence",
                                        "Channel.Evidence","Ms1.Total.Signal.Before","Ms1.Total.Signal.After",
                                        "RT.Start","RT.Stop","FWHM","PG.TopN","PG.MaxLFQ","Genes.TopN",
                                        "Genes.MaxLFQ","Genes.MaxLFQ.Unique","PG.MaxLFQ.Quality",
                                        "Genes.MaxLFQ.Quality","Genes.MaxLFQ.Unique.Quality","Q.Value",
                                        "PEP","Global.Q.Value","Lib.Q.Value","Peptidoform.Q.Value",
                                        "Global.Peptidoform.Q.Value","Lib.Peptidoform.Q.Value",
                                        "PTM.Site.Confidence","Site.Occupancy.Probabilities","Protein.Sites",
                                        "Lib.PTM.Site.Confidence","Translated.Q.Value","Channel.Q.Value",
                                        "PG.Q.Value","PG.PEP","GG.Q.Value","Lib.PG.Q.Value"
                                        ],inplace=True,errors="ignore")
                    
                searchoutput["EG.ModifiedPeptide"]=searchoutput["EG.ModifiedPeptide"].str.replace("(","[")
                searchoutput["EG.ModifiedPeptide"]=searchoutput["EG.ModifiedPeptide"].str.replace(")","]")
                searchoutput["EG.ModifiedPeptide"]=searchoutput["EG.ModifiedPeptide"].replace({
                        "UniMod:1":"Acetyl (Protein N-term)",
                        "UniMod:4":"Carbamidomethyl (C)",
                        "UniMod:21":"Phospho (STY)",
                        "UniMod:35":"Oxidation (M)"},regex=True)

        #this line is needed for some files since some will order the search report by file name and others won't. Need to account for this
        searchoutput_secondary=searchoutput.sort_values('R.FileName')

        return searchoutput_secondary
    
    #upload filled out metadata table
    @reactive.calc
    def inputmetadata_secondary():
        if input.metadata_upload_secondary() is None:
            metadata=pd.DataFrame(columns=["R.FileName","R.Condition","R.Replicate","remove"])
            return metadata
        else:
            metadata=pd.read_csv(input.metadata_upload_secondary()[0]["datapath"],sep=",")
        return metadata
    
    #render the metadata table in the window
    @render.data_frame
    def metadata_table_secondary():
        if input.use_uploaded_metadata_secondary()==True:
            metadata=inputmetadata_secondary()
            if metadata is None:
                metadata=pd.DataFrame(columns=["R.FileName","R.Condition","R.Replicate","remove"])
            metadata=metadata.drop(columns=["order","Concentration"])
        else:
            searchoutput=inputfile_secondary()
            if input.searchreport_secondary() is None:
                metadata=pd.DataFrame(columns=["R.FileName","R.Condition","R.Replicate","remove"])
                return render.DataGrid(metadata,width="100%")
            metadata=pd.DataFrame(searchoutput[["R.FileName","R.Condition","R.Replicate"]]).drop_duplicates().reset_index(drop=True)
            metadata["remove"]=metadata.apply(lambda _: '', axis=1)

        return render.DataGrid(metadata,editable=True,width="100%")

    @render.data_frame
    def metadata_condition_table_secondary():
        if input.use_uploaded_metadata_secondary()==True:
            metadata=inputmetadata_secondary()
            if metadata is None:
                metadata_condition=pd.DataFrame(columns=["R.Condition","order","Concentration"])
            if input.remove_secondary()==True:
                metadata=metadata[metadata.remove !="x"]
            metadata_condition=pd.DataFrame()
            metadata_condition["R.Condition"]=metadata["R.Condition"].drop_duplicates()
            metadata_condition["order"]=metadata["order"].drop_duplicates()
            metadata_condition["Concentration"]=metadata["Concentration"].drop_duplicates()
        else:
            metadata=metadata_table_secondary.data_view()
            if input.searchreport_secondary() is None:
                metadata_condition=pd.DataFrame(columns=["R.Condition","order","Concentration"])
                return render.DataGrid(metadata_condition,width="100%")
            if input.remove_secondary()==True:
                metadata=metadata[metadata.remove !="x"]
            metadata_condition=pd.DataFrame(metadata[["R.Condition"]]).drop_duplicates().reset_index(drop=True)
            metadata_condition["order"]=metadata_condition.apply(lambda _: '', axis=1)
            metadata_condition["Concentration"]=metadata_condition.apply(lambda _: '', axis=1)

        return render.DataGrid(metadata_condition,editable=True,width="100%")

    #give a reminder for what to do with search reports from different software
    @render.text
    def metadata_reminder_secondary():
        if input.software_secondary()=="spectronaut":
            return "Use the Shiny report format when exporting search results. R.Condition and R.Replicate are automatically updated in the metadata based on this file. Click on 'Apply Changes' even if the metadata table was not updated."
        if input.software_secondary()=="diann":
            return "Use the report.tsv file as the file input. Make sure to fill out R.Condition and R.Replicate columns in the metadata and click on 'Apply Changes' after selecting the necessary switches."
        if input.software_secondary()=="diann2.0":
            return "Use the report.parquet file as the file input. Make sure to fill out R.Condition and R.Replicate columns in the metadata and click on 'Apply Changes' after selecting the necessary switches."
        if input.software_secondary()=="ddalibrary":
            return "DDA libraries have limited functionality, can only plot ID metrics."
        if input.software_secondary()=="fragpipe":
            return "Use the psm.tsv file as the file input. Make sure to fill out R.Condition and R.Replicate columns in the metadata and click on 'Apply Changes' after selecting the necessary switches."
        if input.software_secondary()=="fragpipe_glyco":
            return "Use the psm.tsv file as the file input. Make sure to fill out R.Condition and R.Replicate columns in the metadata and click on 'Apply Changes' after selecting the necessary switches. Use the Glycoproteomics tab for processing."
        if input.software_secondary()=="bps_timsrescore":
            return "Use the .zip file from the artefacts download. Make sure to fill out R.Condition and R.Replicate columns in the metadata and click on 'Apply Changes' after selecting the necessary switches."
        if input.software_secondary()=="bps_timsdiann":
            return "Use the .zip file from the artefacts download. Make sure to fill out R.Condition and R.Replicate columns in the metadata and click on 'Apply Changes' after selecting the necessary switches."

    #download metadata table as shown
    @render.download(filename="metadata_"+str(date.today())+".csv")
    def metadata_download_secondary():
        metadata=metadata_table_secondary.data_view()
        metadata_condition=metadata_condition_table_secondary.data_view()

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

    #update the searchoutput df to match how we edited the metadata sheet
    @reactive.calc
    @reactive.event(input.rerun_metadata_secondary,ignore_none=False)
    def metadata_update_secondary():
        searchoutput=inputfile_secondary()
        metadata=metadata_table_secondary.data_view()
        metadata_condition=metadata_condition_table_secondary.data_view()

        if input.condition_names_secondary()==True:
            RConditionlist=[]
            RReplicatelist=[]
            for run in searchoutput["R.FileName"].drop_duplicates().tolist():
                fileindex=metadata[metadata["R.FileName"]==run].index.values[0]
                RConditionlist.append([metadata["R.Condition"][fileindex]]*len(searchoutput.set_index("R.FileName").loc[run]))
                RReplicatelist.append([metadata["R.Replicate"][fileindex]]*len(searchoutput.set_index("R.FileName").loc[run]))
            searchoutput["R.Condition"]=list(itertools.chain(*RConditionlist))
            searchoutput["R.Replicate"]=list(itertools.chain(*RReplicatelist))
            searchoutput["R.Replicate"]=searchoutput["R.Replicate"].astype(int)

        if input.remove_secondary()==True:
            editedmetadata=metadata[metadata.remove !="x"]
            searchoutput=searchoutput.set_index("R.FileName").loc[editedmetadata["R.FileName"].tolist()].reset_index()

        if input.reorder_secondary()==True:
            metadata_condition["order"]=metadata_condition["order"].astype(int)
            sortedmetadata_bycondition=metadata_condition.sort_values(by="order").reset_index(drop=True)
            searchoutput=searchoutput.set_index("R.Condition").loc[sortedmetadata_bycondition["R.Condition"].tolist()].reset_index()

        if input.concentration_secondary()==True:
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

        searchoutput["R.Condition"]=searchoutput["R.Condition"].apply(str)
        if "Cond_Rep" not in searchoutput.columns:
            searchoutput.insert(0,"Cond_Rep",searchoutput["R.Condition"]+"_"+searchoutput["R.Replicate"].apply(str))
        elif "Cond_Rep" in searchoutput.columns:
            searchoutput["Cond_Rep"]=searchoutput["R.Condition"]+"_"+searchoutput["R.Replicate"].apply(str)

        searchoutput_secondary=searchoutput
        return searchoutput_secondary

    #endregion
    
    #calculations for setting up dfs for comparison
    @reactive.calc
    def software_comparison():
        #de novo
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
        #secondary software
        searchoutput_secondary=metadata_update_secondary()

        #make dfs to use in later calculations, drop duplicates to only have unique sequences to each run
        bps_df=searchoutput[["Cond_Rep","PEP.StrippedSequence","found_in_fasta"]].drop_duplicates().reset_index(drop=True)
        secondary_df=searchoutput_secondary[["Cond_Rep","PEP.StrippedSequence"]].drop_duplicates().reset_index(drop=True)

        #convert Ile to Leu in secondary software (BPS can't differentiate, only writes Leu)
        peplist_subItoL=[]
        for pep in secondary_df["PEP.StrippedSequence"]:
            peplist_subItoL.append(pep.replace("I","L"))
        secondary_df["PEP.StrippedSequence"]=peplist_subItoL

        #calculate and add peptide lengths column to both dfs
        bps_peplen=[]
        for pep in bps_df["PEP.StrippedSequence"]:
            bps_peplen.append(len(pep))
        bps_df["Peptide Length"]=bps_peplen

        secondary_peplen=[]
        for pep in secondary_df["PEP.StrippedSequence"]:
            secondary_peplen.append(len(pep))
        secondary_df["Peptide Length"]=secondary_peplen

        return bps_df,secondary_df

    # ====================================== Compare - Peptide Lengths
    #render ui call for dropdown calling Cond_Rep column
    @render.ui
    def compare_len_samplelist():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
        opts=resultdf["Cond_Rep"].tolist()
        return ui.input_selectize("compare_len_samplelist_pick","Pick run:",choices=opts)
    #bar graph for comparing lengths of detected peptides between BPS Novor and other software
    @reactive.effect
    def _():
        @render.plot(width=input.peplength_compare_width(),height=input.peplength_compare_height())
        def peplength_compare_plot():
            bps_df,secondary_df=software_comparison()

            run=input.compare_len_samplelist_pick()
            axisfont=input.axisfont()
            titlefont=input.titlefont()
            legendfont=input.legendfont()

            bps_df=bps_df[bps_df["Cond_Rep"]==run]
            secondary_df=secondary_df[secondary_df["Cond_Rep"]==run]

            #secondary software lengths and counts for plotting IDs and unique de novo IDs
            secondary_x=list(set(itertools.chain(*[list(group) for key, group in groupby(sorted(secondary_df["Peptide Length"]))])))
            secondary_y=[len(list(group)) for key, group in groupby(sorted(secondary_df["Peptide Length"]))]
            secondary_len_counts=pd.DataFrame()
            secondary_len_counts["Peptide Length"]=secondary_x
            secondary_len_counts["Secondary"]=secondary_y
            secondary_len_counts=secondary_len_counts.set_index("Peptide Length")

            #intersections of the two software
            A=set(secondary_df["PEP.StrippedSequence"])
            B=set(bps_df["PEP.StrippedSequence"])

            AvsB=list(A-B)
            BvsA=list(B-A)

            AnotB=len(A-B)
            BnotA=len(B-A)
            bothAB=len(A&B)

            #build a df of just the peptides unique to denovo
            unique_to_denovo=pd.DataFrame()
            unique_to_denovo=pd.concat([unique_to_denovo,pd.Series(BvsA,name="PEP.StrippedSequence")],axis=1)
            unique_peplen=[]
            for pep in unique_to_denovo["PEP.StrippedSequence"]:
                unique_peplen.append(len(pep))
            unique_to_denovo["Peptide Length"]=unique_peplen
            unique_to_denovo_x=list(set(itertools.chain(*[list(group) for key, group in groupby(sorted(unique_to_denovo["Peptide Length"]))])))
            unique_to_denovo_y=[len(list(group)) for key, group in groupby(sorted(unique_to_denovo["Peptide Length"]))]
            unique_to_denovo_len_counts=pd.DataFrame()
            unique_to_denovo_len_counts["Peptide Length"]=unique_to_denovo_x
            unique_to_denovo_len_counts["Denovo Unique"]=unique_to_denovo_y
            unique_to_denovo_len_counts=unique_to_denovo_len_counts.set_index("Peptide Length")

            peplengths_combined=pd.concat([secondary_len_counts,unique_to_denovo_len_counts],axis=1).sort_values("Peptide Length").fillna(0)
            peplengths_combined
            fig,ax=plt.subplots()
            x=list(peplengths_combined.index)
            ax.bar(x,peplengths_combined["Secondary"],label="Fragger")
            ax.bar(x,peplengths_combined["Denovo Unique"],label="BPS Novor (Unique)",bottom=peplengths_combined["Secondary"])
            ax.legend(loc="upper right",fontsize=legendfont)
            ax.xaxis.set_major_locator(MultipleLocator(2))
            ax.set_title(run,fontsize=titlefont)
            ax.set_xlabel("Peptide Length",fontsize=axisfont)
            ax.set_ylabel("Counts",fontsize=axisfont)
            ax.set_ylim(bottom=-(0.025*ax.get_ylim()[1]))
            ax.set_axisbelow(True)
            ax.grid(linestyle="--")

    # ====================================== Compare - Stripped Peptide IDs
    #render ui call for dropdown calling Cond_Rep column
    @render.ui
    def denovocompare_venn_samplelist():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
        opts=resultdf["Cond_Rep"].tolist()
        return ui.input_selectize("denovocompare_venn_samplelist_pick","Pick run:",choices=opts)
    @render.ui
    def denovocompare_specific_length_ui():
        if input.denovocompare_specific_length()==True:
            return ui.input_slider("denovocompare_specific_length_pick","Pick specific peptide length to compare:",min=3,max=30,value=9,step=1,ticks=True)
    #plot venn diagram of stripped peptide IDs between the two software
    @reactive.effect
    def _():
        @render.plot(width=input.denovocompare_venn_width(),height=input.denovocompare_venn_height())
        def denovocompare_venn_plot():
            bps_df,secondary_df=software_comparison()

            run=input.denovocompare_venn_samplelist_pick()
            titlefont=input.titlefont()

            if input.software_secondary()=="spectronaut":
                name_mod="Spectronaut"
            if input.software_secondary()=="diann":
                name_mod="DIA-NN"
            if input.software_secondary()=="diann2.0":
                name_mod="DIA-NN 2.0"
            if input.software_secondary()=="fragpipe":
                name_mod="FragPipe"
            if input.software_secondary()=="bps_timsrescore":
                name_mod="tims-Rescore"
            if input.software_secondary()=="bps_timsdiann":
                name_mod="tims-DIANN"

            if input.denovocompare_specific_length()==True:
                bps_df=bps_df[(bps_df["Cond_Rep"]==run)&(bps_df["Peptide Length"]==int(input.denovocompare_specific_length_pick()))]
                secondary_df=secondary_df[(secondary_df["Cond_Rep"]==run)&(secondary_df["Peptide Length"]==int(input.denovocompare_specific_length_pick()))]
                titlemod=" "+str(input.denovocompare_specific_length_pick())+"mers"
            else:
                bps_df=bps_df[bps_df["Cond_Rep"]==run]
                secondary_df=secondary_df[secondary_df["Cond_Rep"]==run]
                titlemod=""

            if input.denovocompare_peptidecore()==True:
                bps_df_coreAA=[]
                secondary_df_coreAA=[]
                for pep in bps_df["PEP.StrippedSequence"].tolist():
                    bps_df_coreAA.append(pep[2:-2])
                for pep in secondary_df["PEP.StrippedSequence"].tolist():
                    secondary_df_coreAA.append(pep[2:-2])
                A=set(secondary_df_coreAA)
                B=set(bps_df_coreAA)

            else:
                #intersections of the two software
                A=set(secondary_df["PEP.StrippedSequence"])
                B=set(bps_df["PEP.StrippedSequence"])

            AvsB=list(A-B)
            BvsA=list(B-A)

            AnotB=len(A-B)
            BnotA=len(B-A)
            bothAB=len(A&B)

            fig,ax=plt.subplots()
            vennlist=[AnotB,BnotA,bothAB]
            venn2(subsets=vennlist,set_labels=(name_mod,"BPS Novor"),set_colors=("tab:blue","tab:orange"),ax=ax)
            venn2_circles(subsets=vennlist,linestyle="dashed",linewidth=0.5)
            plt.title(run+" Stripped Peptide IDs"+titlemod,fontsize=titlefont)
    #download list of common and unique IDs
    @render.download(filename=lambda: f'{input.denovocompare_venn_samplelist_pick()}_BPSNovor_Venn.csv')
    def denovocompare_venn_download():
        bps_df,secondary_df=software_comparison()

        run=input.denovocompare_venn_samplelist_pick()
        titlefont=input.titlefont()

        if input.software_secondary()=="spectronaut":
            name_mod="Spectronaut"
        if input.software_secondary()=="diann":
            name_mod="DIA-NN"
        if input.software_secondary()=="diann2.0":
            name_mod="DIA-NN 2.0"
        if input.software_secondary()=="fragpipe":
            name_mod="FragPipe"
        if input.software_secondary()=="bps_timsrescore":
            name_mod="tims-Rescore"
        if input.software_secondary()=="bps_timsdiann":
            name_mod="tims-DIANN"   

        if input.denovocompare_specific_length()==True:
            bps_df=bps_df[(bps_df["Cond_Rep"]==run)&(bps_df["Peptide Length"]==int(input.denovocompare_specific_length_pick()))]
            secondary_df=secondary_df[(secondary_df["Cond_Rep"]==run)&(secondary_df["Peptide Length"]==int(input.denovocompare_specific_length_pick()))]
        else:
            bps_df=bps_df[bps_df["Cond_Rep"]==run]
            secondary_df=secondary_df[secondary_df["Cond_Rep"]==run]

        if input.denovocompare_peptidecore()==True:
            bps_df_coreAA=[]
            secondary_df_coreAA=[]
            for pep in bps_df["PEP.StrippedSequence"].tolist():
                bps_df_coreAA.append(pep[2:-2])
            for pep in secondary_df["PEP.StrippedSequence"].tolist():
                secondary_df_coreAA.append(pep[2:-2])
            A=set(secondary_df_coreAA)
            B=set(bps_df_coreAA)

        else:
            #intersections of the two software
            A=set(secondary_df["PEP.StrippedSequence"])
            B=set(bps_df["PEP.StrippedSequence"])

        AvsB=list(A-B)
        BvsA=list(B-A)
        ABcommon=list(A&B)

        AnotB=len(A-B)
        BnotA=len(B-A)
        bothAB=len(A&B)

        unique_ids_df=pd.DataFrame()
        unique_ids_df=pd.concat([unique_ids_df,pd.Series(ABcommon,name="Common IDs"),pd.Series(AvsB,name=name_mod+" Unique"),pd.Series(BvsA,name="BPS Novor Unique")],axis=1)

        with io.BytesIO() as buf:
            unique_ids_df.to_csv(buf,index=False)
            yield buf.getvalue()

    # ====================================== Compare - Sequence Motifs
    @render.ui
    def seqmotif_compare_run_ui():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
        opts=resultdf["Cond_Rep"].tolist()
        return ui.input_selectize("seqmotif_compare_run_pick","Pick run:",choices=opts)
    #BPS sequence motif plot
    @render.plot(width=800,height=400)
    def seqmotif_compare_plot1():
        bps_df,secondary_df=software_comparison()
        titlefont=input.titlefont()
        axisfont=input.axisfont()

        if input.seqmotif_compare_onlyunique()==False:
            seq=bps_df[(bps_df["Cond_Rep"]==input.seqmotif_compare_run_pick())&(bps_df["Peptide Length"]==input.seqmotif_compare_peplengths())]["PEP.StrippedSequence"].drop_duplicates().tolist()
            titlemod=""
        if input.seqmotif_compare_onlyunique()==True:
            titlemod=" Only Unique IDs"
            bps_df=bps_df[(bps_df["Cond_Rep"]==input.seqmotif_compare_run_pick())&(bps_df["Peptide Length"]==int(input.seqmotif_compare_peplengths()))]
            secondary_df=secondary_df[(secondary_df["Cond_Rep"]==input.seqmotif_compare_run_pick())&(secondary_df["Peptide Length"]==int(input.seqmotif_compare_peplengths()))]
            A=set(secondary_df["PEP.StrippedSequence"])
            B=set(bps_df["PEP.StrippedSequence"])
            seq=list(A-B)

        matrix=lm.alignment_to_matrix(seq)
        if input.seqmotif_compare_plottype()=="counts":
            ylabel="Counts"
        if input.seqmotif_compare_plottype()=="information":
            matrix=lm.transform_matrix(matrix,from_type="counts",to_type="information")
            ylabel="Information (bits)"
        logo=lm.Logo(matrix,vsep=0.01,vpad=0.01,color_scheme="weblogo_protein")
        logo.ax.set_xlabel("Position",fontsize=axisfont)
        logo.ax.set_ylabel(ylabel,fontsize=axisfont)
        logo.ax.set_title("BPS "+input.seqmotif_compare_run_pick()+": "+str(input.seqmotif_peplengths())+"mers"+titlemod,fontsize=titlefont)
        logo.ax.set_ylim(bottom=0)
    #secondary sequence motif plot
    @render.plot(width=800,height=400)
    def seqmotif_compare_plot2():
        bps_df,secondary_df=software_comparison()

        seq2=secondary_df[(secondary_df["Cond_Rep"]==input.seqmotif_compare_run_pick())&(secondary_df["Peptide Length"]==input.seqmotif_compare_peplengths())]["PEP.StrippedSequence"].drop_duplicates().tolist()
        titlefont=input.titlefont()
        axisfont=input.axisfont()

        if input.software_secondary()=="spectronaut":
            name_mod="Spectronaut"
        if input.software_secondary()=="diann":
            name_mod="DIA-NN"
        if input.software_secondary()=="diann2.0":
            name_mod="DIA-NN 2.0"
        if input.software_secondary()=="fragpipe":
            name_mod="FragPipe"
        if input.software_secondary()=="bps_timsrescore":
            name_mod="tims-Rescore"
        if input.software_secondary()=="bps_timsdiann":
            name_mod="tims-DIANN"   

        matrix2=lm.alignment_to_matrix(seq2)
        if input.seqmotif_compare_plottype()=="counts":
            ylabel="Counts"
        if input.seqmotif_compare_plottype()=="information":
            matrix2=lm.transform_matrix(matrix2,from_type="counts",to_type="information")
            ylabel="Information (bits)"
        logo2=lm.Logo(matrix2,vsep=0.01,vpad=0.01,color_scheme="weblogo_protein")
        logo2.ax.set_xlabel("Position",fontsize=axisfont)
        logo2.ax.set_ylabel(ylabel,fontsize=axisfont)
        logo2.ax.set_title(name_mod+" "+input.seqmotif_compare_run_pick()+": "+str(input.seqmotif_peplengths())+"mers",fontsize=titlefont)
        logo2.ax.set_ylim(bottom=0)

    # ====================================== Compare - Sequence Motifs (stats)
    @render.ui
    def seqmotif_compare_run_ui2():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
        opts=resultdf["Cond_Rep"].tolist()
        return ui.input_selectize("seqmotif_compare_run_pick2","Pick run:",choices=opts)
    #PCA plot
    @render.plot(height=600)
    def seqmotif_pca():
        bps_df,secondary_df=software_comparison()

        seq_BPS=bps_df[(bps_df["Cond_Rep"]==input.seqmotif_compare_run_pick2())&(bps_df["Peptide Length"]==int(input.seqmotif_compare_peplengths2()))]["PEP.StrippedSequence"].drop_duplicates().tolist()
        seq_secondary=secondary_df[(secondary_df["Cond_Rep"]==input.seqmotif_compare_run_pick2())&(secondary_df["Peptide Length"]==int(input.seqmotif_compare_peplengths2()))]["PEP.StrippedSequence"].drop_duplicates().tolist()

        if input.software_secondary()=="spectronaut":
            name_mod="Spectronaut"
        if input.software_secondary()=="diann":
            name_mod="DIA-NN"
        if input.software_secondary()=="diann2.0":
            name_mod="DIA-NN 2.0"
        if input.software_secondary()=="fragpipe":
            name_mod="FragPipe"
        if input.software_secondary()=="bps_timsrescore":
            name_mod="tims-Rescore"
        if input.software_secondary()=="bps_timsdiann":
            name_mod="tims-DIANN"

        if input.seqmotif_compare_onlyunique2()==True:
            a=set(seq_secondary)
            b=set(seq_BPS)
            seq_BPS=list(a-b)
            B=lm.alignment_to_matrix(seq_BPS,to_type="information")
            titlemod=" Only Unique BPS IDs"
        if input.seqmotif_compare_onlyunique2()==False:
            B=lm.alignment_to_matrix(seq_BPS,to_type="information")
            titlemod=""

        A=lm.alignment_to_matrix(seq_secondary,to_type="information")
        for col in A.columns.tolist():
            A=A.rename(columns={col:str(col)+"_secondary"})
        for col in B.columns.tolist():
            B=B.rename(columns={col:str(col)+"_BPS"})
        concatenated=pd.concat([A,B],axis=1)

        X=np.array(concatenated).T
        pip=Pipeline([("scaler",StandardScaler()),("pca",PCA())]).fit(X)
        X_trans=pip.transform(X)

        fig,ax=plt.subplots()

        colors=["firebrick","red","lightcoral","orange","gold","goldenrod","green","lime","darkturquoise","cyan",
                "dodgerblue","lightsteelblue","blue","blueviolet","purple","fuchsia","violet","pink","slategrey"]
        for i in range(len(concatenated.columns.tolist())):
            if i>18:
                z=i-19
                label="B"
            else:
                z=i
                label="S"
            ax.scatter(X_trans[i,0],X_trans[i,1],color=colors[z],s=45,label=concatenated.columns.tolist()[i].split("_")[0])
            ax.annotate(label,(X_trans[i,0]+0.05,X_trans[i,1]+0.05),fontsize=8)
        ax.set_xlabel("PC1"+" ("+str(round(pip.named_steps.pca.explained_variance_ratio_[0]*100,1))+"%)")
        ax.set_ylabel("PC2"+" ("+str(round(pip.named_steps.pca.explained_variance_ratio_[1]*100,1))+"%)")
        handles,labels=ax.get_legend_handles_labels()
        handle_list,label_list =[],[]
        for handle,label in zip(handles,labels):
            if label not in label_list:
                handle_list.append(handle)
                label_list.append(label)
        ax.legend(handle_list,label_list,loc="center",bbox_to_anchor=(1.1,0.5),markerscale=1)
        ax.set_title("BPS vs. "+name_mod+": "+input.seqmotif_compare_run_pick2()+" "+str(input.seqmotif_compare_peplengths2())+"mers"+titlemod)
        fig.set_tight_layout(True)
    #3D plot
    @render.plot(height=600)
    def seqmotif_3d():
        bps_df,secondary_df=software_comparison()

        axisfont=input.axisfont()

        if input.software_secondary()=="spectronaut":
            name_mod="Spectronaut"
        if input.software_secondary()=="diann":
            name_mod="DIA-NN"
        if input.software_secondary()=="diann2.0":
            name_mod="DIA-NN 2.0"
        if input.software_secondary()=="fragpipe":
            name_mod="FragPipe"
        if input.software_secondary()=="bps_timsrescore":
            name_mod="tims-Rescore"
        if input.software_secondary()=="bps_timsdiann":
            name_mod="tims-DIANN"

        seq_BPS=bps_df[(bps_df["Cond_Rep"]==input.seqmotif_compare_run_pick2())&(bps_df["Peptide Length"]==int(input.seqmotif_compare_peplengths2()))]["PEP.StrippedSequence"].drop_duplicates().tolist()
        seq_secondary=secondary_df[(secondary_df["Cond_Rep"]==input.seqmotif_compare_run_pick2())&(secondary_df["Peptide Length"]==int(input.seqmotif_compare_peplengths2()))]["PEP.StrippedSequence"].drop_duplicates().tolist()

        if input.seqmotif_compare_onlyunique2()==True:
            a=set(seq_secondary)
            b=set(seq_BPS)
            seq_BPS=list(a-b)
            B=lm.alignment_to_matrix(seq_BPS,to_type="information")
            titlemod=" Only Unique BPS IDs"
        if input.seqmotif_compare_onlyunique2()==False:
            B=lm.alignment_to_matrix(seq_BPS,to_type="information")
            titlemod=""

        A=lm.alignment_to_matrix(seq_secondary,to_type="information")
        
        xdata=np.arange(1,20).tolist()
        ydata=np.arange(1,1+int(input.seqmotif_compare_peplengths2())).tolist()
        columns=A.columns.tolist()
        colors=["firebrick","red","lightcoral","orange","gold","goldenrod","green","lime","darkturquoise","cyan",
                "dodgerblue","lightsteelblue","blue","blueviolet","purple","fuchsia","violet","pink","slategrey"]
        fig=plt.figure()
        ax=fig.add_subplot(111,projection='3d')
        for i in range(len(columns)):
            zdata_BPS=B[columns[i]]
            zdata_fragger=A[columns[i]]
            if i>18:
                z=i-19
            else:
                z=i
            ax.scatter(xdata[i],ydata,zdata_BPS,color=colors[z],label=columns[i])
            ax.scatter(xdata[i],ydata,zdata_fragger,color=colors[z])
        ax.view_init(azim=input.seqmotif_3d_azimuth(),elev=input.seqmotif_3d_elevation())
        ax.set_xticks(xdata,columns)
        ax.set_xlabel("Residue")
        ax.set_ylabel("Position")
        ax.legend(loc="center",bbox_to_anchor=(1.1,0.5))
        ax.set_title("BPS vs. "+name_mod+": "+input.seqmotif_compare_run_pick2()+" "+str(input.seqmotif_compare_peplengths2())+"mers"+titlemod)
        fig.set_tight_layout(True)

    # ====================================== IDs Found in Fasta
    @reactive.effect
    def _():
        @render.plot(width=input.fasta_width(),height=input.fasta_height())
        def fasta_plot():
            searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
            cond_rep_list=searchoutput["Cond_Rep"].drop_duplicates().tolist()
            fasta_df=pd.DataFrame()
            fasta_true=[]
            fasta_false=[]
            for run in cond_rep_list:
                df=searchoutput[searchoutput["Cond_Rep"]==run]
                fasta_false.append(len(df[df["found_in_fasta"]==False]))
                fasta_true.append(len(df[df["found_in_fasta"]==True]))
            fasta_df["Cond_Rep"]=cond_rep_list
            fasta_df["Fasta_True"]=fasta_true
            fasta_df["Fasta_False"]=fasta_false

            fig,ax=plt.subplots()
            x=np.arange(len(fasta_df))
            width=0.4
            
            labelfont=input.labelfont()
            axisfont=input.axisfont()
            legendfont=input.legendfont()     
            y_padding=input.ypadding()

            maxvalue=max(fasta_df[["Fasta_True","Fasta_False"]].max().tolist())
            ax.bar(x,fasta_df["Fasta_True"],width=width,label="Fasta=True",edgecolor="k")
            ax.bar(x+width,fasta_df["Fasta_False"],width=width,label="Fasta=False",edgecolor="k")

            ax.bar_label(ax.containers[0],label_type="edge",padding=5,rotation=90,fontsize=labelfont)
            ax.bar_label(ax.containers[1],label_type="edge",padding=5,rotation=90,fontsize=labelfont)
            ax.set_xticks(x+(width/2),fasta_df["Cond_Rep"],rotation=input.xaxis_label_rotation())
            ax.set_ylim(top=maxvalue+(y_padding*maxvalue))
            ax.margins(x=0.02)
            ax.set_xlabel("Run",fontsize=axisfont)
            ax.set_ylabel("Counts",fontsize=axisfont)
            ax.legend(fontsize=legendfont)
            ax.set_axisbelow(True)
            ax.grid(linestyle="--")

    # ====================================== Position Confidence
    @render.ui
    def confidence_condition_ui():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
        opts=sampleconditions
        return ui.input_selectize("confidence_condition_pick","Pick sample condition:",choices=opts)
    @reactive.effect
    def _():
        @render.plot(width=input.confidence_width(),height=input.confidence_height())
        def confidence_plot():
            peplen=input.confidence_lengthslider()
            axisfont=input.axisfont()
            titlefont=input.titlefont()

            searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
            listoflengths=[]
            for pep in searchoutput["PEP.StrippedSequence"]:
                listoflengths.append(len(pep))
            searchoutput_len=searchoutput
            searchoutput_len["Peptide Length"]=listoflengths

            condition_pick=input.confidence_condition_pick()
            confidence_plot_df=searchoutput_len[searchoutput_len["R.Condition"]==condition_pick]

            fig,ax=plt.subplots(nrows=len(confidence_plot_df["Cond_Rep"].drop_duplicates()),sharex=True)

            for i,run in enumerate(confidence_plot_df["Cond_Rep"].drop_duplicates().tolist()):

                df=confidence_plot_df[(confidence_plot_df["Cond_Rep"]==run)&(confidence_plot_df["Peptide Length"]==peplen)]
                columns=list(np.arange(peplen).astype(str))
                denovo_confidence_df=pd.DataFrame(df["denovo_local_confidence"].tolist(),columns=columns)
                
                position_confidence=[]
                for col in denovo_confidence_df.columns:
                    position_confidence.append(denovo_confidence_df[col].tolist())
                plottingdf=pd.DataFrame()
                plottingdf["Position"]=columns
                plottingdf["Confidence"]=position_confidence

                medianlineprops=dict(linestyle="--",color="black")
                flierprops=dict(markersize=3)
                bplot=ax[i].boxplot(plottingdf["Confidence"],medianprops=medianlineprops,flierprops=flierprops,patch_artist=True)
                ax[i].set_ylabel("Confidence (%)",fontsize=axisfont)
                ax[i].set_title(run,fontsize=titlefont)
                
                ax[i].set_axisbelow(True)
                ax[i].grid(linestyle="--")
                
                colors=mcolors.TABLEAU_COLORS
                for patch,color in zip(bplot["boxes"],colors):
                    patch.set_facecolor(color)
            plt.xlabel("Position",fontsize=axisfont)
            fig.set_tight_layout(True)

#endregion

# ============================================================================= Two-Software Comparison
#region
    # ====================================== File Import
    #import first search report file
    @reactive.calc
    def compare_inputfile1():
        if input.compare_searchreport1() is None:
            return pd.DataFrame()
        if ".tsv" in input.compare_searchreport1()[0]["name"]:
            if len(input.compare_searchreport1())>1:
                searchoutput=pd.DataFrame()
                for i in range(len(input.compare_searchreport1())):
                    run=pd.read_csv(input.compare_searchreport1()[i]["datapath"],sep="\t")
                    searchoutput=pd.concat([searchoutput,run])
            else:
                searchoutput=pd.read_csv(input.compare_searchreport1()[0]["datapath"],sep="\t")
            if input.compare_software1()=="diann":
                searchoutput.rename(columns={"Run":"R.FileName"},inplace=True)
                searchoutput.insert(1,"R.Condition","")
                searchoutput.insert(2,"R.Replicate","")
                searchoutput["EG.PeakWidth"]=searchoutput["RT.Stop"]-searchoutput["RT.Start"]

                searchoutput.drop(columns=["File.Name","PG.Normalized","PG.MaxLFQ","Genes.Quantity",
                                            "Genes.Normalised","Genes.MaxLFQ","Genes.MaxLFQ.Unique","Precursor.Id",
                                            "PEP","Global.Q.Value","GG.Q.Value",#"Protein.Q.Value","Global.PG.Q.Value",
                                            "Translated.Q.Value","Precursor.Translated","Translated.Quality","Ms1.Translated",
                                            "Quantity.Quality","RT.Stop","RT.Start","iRT","Predicted.iRT",
                                            "First.Protein.Description","Lib.Q.Value","Lib.PG.Q.Value","Ms1.Profile.Corr",
                                            "Ms1.Area","Evidence","Spectrum.Similarity","Averagine","Mass.Evidence",
                                            "Decoy.Evidence","Decoy.CScore","Fragment.Quant.Raw","Fragment.Quant.Corrected",
                                            "Fragment.Correlations","MS2.Scan","iIM","Predicted.IM",
                                            "Predicted.iIM","PG.Normalised","PTM.Informative","PTM.Specific","PTM.Localising",
                                            "PTM.Q.Value","PTM.Site.Confidence","Lib.PTM.Site.Confidence"],inplace=True,errors='ignore')

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
                        "UniMod:7":"Deamidation (NQ)",
                        "UniMod:21":"Phospho (STY)",
                        "UniMod:35":"Oxidation (M)"},regex=True)
            if input.compare_software1()=="ddalibrary":
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
            if input.compare_software1()=="fragpipe":
                searchoutput.rename(columns={"Spectrum File":"R.FileName"},inplace=True)
                searchoutput.insert(1,"R.Condition","")
                searchoutput.insert(2,"R.Replicate","")
                
                searchoutput["FG.CalibratedMassAccuracy (PPM)"]=(searchoutput["Delta Mass"]/searchoutput["Calculated M/Z"])*10E6

                searchoutput.drop(columns=["Spectrum","Extended Peptide","Prev AA","Next AA","Peptide Length",
                                        "Observed Mass","Calibrated Observed Mass","Calibrated Observed M/Z",
                                        "Calculated Peptide Mass","Calculated M/Z","Delta Mass",
                                        "Expectation","Hyperscore","Nextscore",
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
                    "43":"Acetyl (Protein N-term)",
                    "111":""},regex=True)

                peps=searchoutput["PEP.StrippedSequence"].tolist()
                modpeps=searchoutput["EG.ModifiedPeptide"].tolist()
                for i in range(len(peps)):
                    if type(modpeps[i])!=str:
                        modpeps[i]=peps[i]
                    else:
                        modpeps[i]=modpeps[i]
                searchoutput["EG.ModifiedPeptide"]=modpeps
            if input.compare_software1()=="fragpipe_glyco":
                #if the Spectrum File column is just a single value, get the file names from the Spectrum column
                if searchoutput["Spectrum"][0].split(".")[0] not in searchoutput["Spectrum File"][0]:
                    fragger_filelist=searchoutput["Spectrum"].str.split(".",expand=True).drop(columns=[1,2,3]).drop_duplicates().reset_index(drop=True)
                    fragger_filelist.rename(columns={0:"R.FileName"},inplace=True)

                    filenamelist=[]
                    for run in fragger_filelist["R.FileName"]:
                        fileindex=fragger_filelist[fragger_filelist["R.FileName"]==run].index.values[0]
                        filenamelist.append([fragger_filelist["R.FileName"][fileindex]]*len(searchoutput[searchoutput["Spectrum"].str.contains(run)]))

                    searchoutput.insert(0,"R.FileName",list(itertools.chain(*filenamelist)))
                    searchoutput.drop(columns=["Spectrum File"],inplace=True)

                else:
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
        
        #for BPS input
        if ".zip" in input.compare_searchreport1()[0]["name"]:
            if input.compare_software1()=="bps_timsrescore":
                searchoutput=pd.DataFrame()

                bpszip=ZipFile(input.compare_searchreport1()[0]["datapath"])
                bpszip.extractall()
                metadata_bps=pd.read_csv("metadata.csv")
                runlist=metadata_bps["processing_run_uuid"].tolist()
                cwd=os.getcwd()+"\\processing-run"
                os.chdir(cwd)

                peptide_dict=dict()
                samplename_list=[]
                for run in runlist:
                    os.chdir(cwd)
                    os.chdir(cwd+"\\"+run)
                    pgfdr_peptide=pd.read_parquet("pgfdr.peptide.parquet")                   
                    peptide_dict[run]=pgfdr_peptide

                #filter, rename/remove columns, and generate ProteinGroups and ProteinNames columns from protein_list column
                for key in peptide_dict.keys():
                    df=peptide_dict[key][peptide_dict[key]["protein_list"].str.contains("Reverse")==False].reset_index(drop=True)
                    df=df.rename(columns={"sample_name":"R.FileName",
                                    "stripped_peptide":"PEP.StrippedSequence",
                                    "precursor_mz":"FG.PrecMz",
                                    "rt":"EG.ApexRT",
                                    "charge":"FG.Charge",
                                    "ook0":"EG.IonMobility",
                                    "ppm_error":"FG.CalibratedMassAccuracy (PPM)"})

                    proteingroups=[]
                    proteinnames=[]
                    proteinlist_column=df["protein_list"].tolist()
                    for item in proteinlist_column:
                        if item.count(";")==0:
                            templist=item.split("|")
                            proteingroups.append(templist[1])
                            proteinnames.append(templist[2])
                        else:
                            proteingroups_torejoin=[]
                            proteinnames_torejoin=[]
                            for entry in item.split(";"):
                                templist=entry.split("|")
                                proteingroups_torejoin.append(templist[1])
                                proteinnames_torejoin.append(templist[2])
                            proteingroups.append(";".join(proteingroups_torejoin))
                            proteinnames.append(";".join(proteinnames_torejoin))
                    df["PG.ProteinGroups"]=proteingroups
                    df["PG.ProteinNames"]=proteinnames
                    
                    #adding a q-value filter before dropping the column
                    df=df[df["global_peptide_qvalue"]<=0.01]

                    df=df.drop(columns=["index","processing_run_uuid","ms2_id","candidate_id","protein_group_parent_id",
                                    "protein_group_name","leading_aa","trailing_aa","mokapot_psm_score","mokapot_psm_qvalue",
                                    "mokapot_psm_pep","mokapot_peptide_qvalue","mokapot_peptide_pep","global_peptide_score",
                                    "x_corr_score","delta_cn_score","precursor_mh","calc_mh","protein_list","is_contaminant",
                                    "is_target","number_matched_ions","global_peptide_qvalue"],errors='ignore')
                    
                    searchoutput=pd.concat([searchoutput,df],ignore_index=True)

                #rename ptms 
                searchoutput=searchoutput.reset_index(drop=True)
                searchoutput["ptms"]=searchoutput["ptms"].astype(str)
                searchoutput["ptms"]=searchoutput["ptms"].replace({
                        "42.010565":"Acetyl (Protein N-term)",
                        "57.021464":"Carbamidomethyl (C)",
                        "79.966331":"Phospho (STY)",
                        "15.994915":"Oxidation (M)"},regex=True)

                searchoutput["ptm_locations"]=searchoutput["ptm_locations"].astype(str)
                searchoutput["ptm_locations"]=searchoutput["ptm_locations"].str.replace("[]","-1").str.replace("[","").str.replace("]","")

                #build and add the EG.ModifiedPeptide column
                modifiedpeptides=[]
                for i,entry in enumerate(searchoutput["ptm_locations"]):
                    if entry=="-1":
                        modifiedpeptides.append(searchoutput["PEP.StrippedSequence"][i])
                    else:
                        str_to_list=list(searchoutput["PEP.StrippedSequence"][i])
                        if len(searchoutput["ptm_locations"][i])==1:
                            mod_loc=int(searchoutput["ptm_locations"][i])+1
                            mod_add=searchoutput["ptms"][i]
                            str_to_list.insert(mod_loc,mod_add)
                            modifiedpeptides.append("".join(str_to_list))
                        #if theres >1 ptm, we need to reformat some strings so we can insert them in the sequence
                        else:
                            ptmlocs=searchoutput["ptm_locations"][i].strip().split(" ")
                            ptms=searchoutput["ptms"][i].replace("[","").replace("]","").replace(") ","),").split(",")
                            ptms_for_loop=[]
                            for ele in ptms:
                                ptms_for_loop.append("["+ele+"]")
                            for j,loc in enumerate(ptmlocs):
                                mod_loc=int(loc)+j+1
                                mod_add=ptms_for_loop[j]
                                str_to_list.insert(mod_loc,mod_add)
                            modifiedpeptides.append("".join(str_to_list))
                searchoutput["EG.ModifiedPeptide"]=modifiedpeptides
                searchoutput=searchoutput.drop(columns=["ptms","ptm_locations"])

                searchoutput.insert(1,"R.Condition","")
                searchoutput.insert(2,"R.Replicate","")
                
                #change the cwd back to the code file since we changed it to the uploaded file 
                os.chdir(os.path.dirname(os.path.realpath(__file__)))
            if input.compare_software1()=="bps_timsdiann":
                searchoutput=pd.DataFrame()

                bpszip=ZipFile(input.compare_searchreport1()[0]["datapath"])
                bpszip.extractall()
                metadata_bps=pd.read_csv("metadata.csv")
                runlist=metadata_bps["processing_run_uuid"].tolist()
                cwd=os.getcwd()+"\\processing-run"
                os.chdir(cwd)

                for run in runlist:
                    os.chdir(cwd)
                    os.chdir(os.getcwd()+"\\"+run)
                    bps_resultzip=ZipFile("tims-diann.result.zip")
                    bps_resultzip.extractall()
                    results=pd.read_csv("results.tsv",sep="\t")
                    searchoutput=pd.concat([searchoutput,results])

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
                                        "Precursor.Calibrated.Mz","Fragment.Info","Fragment.Calibrated.Mz","Lib.1/K0",
                                        "Precursor.Normalised"],inplace=True,errors='ignore')

                searchoutput.rename(columns={"File.Name":"R.FileName",
                                            "Protein.Group":"PG.ProteinGroups",
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

                searchoutput.insert(1,"R.Condition","")
                searchoutput.insert(2,"R.Replicate","")
                
                #change the cwd back to the code file since we changed it to the uploaded file 
                os.chdir(os.path.dirname(os.path.realpath(__file__)))
            if input.compare_software1()=="bps_denovo":
                denovo_score=65.0

                searchoutput=pd.DataFrame()

                bpszip=ZipFile(input.compare_searchreport1()[0]["datapath"])
                bpszip.extractall()
                metadata_bps=pd.read_csv("metadata.csv")
                runlist=metadata_bps["processing_run_uuid"].tolist()
                cwd=os.getcwd()+"\\processing-run"
                os.chdir(cwd)

                peptide_dict=dict()
                protein_dict=dict()
                for run in runlist:
                    os.chdir(cwd)
                    #change working dir to next processing run subfolder
                    os.chdir(cwd+"\\"+run)

                    peptide_dict[run]=pd.read_parquet("novor-fasta-mapping-results.peptide.parquet")
                    protein_dict[run]=pd.read_parquet("novor-fasta-mapping-results.protein.parquet")

                for key in peptide_dict.keys():
                    peptideparquet=peptide_dict[key]
                    proteinparquet=protein_dict[key]

                    #filter parquet file
                    peptideparquet=peptideparquet[(peptideparquet["denovo_score"]>=denovo_score)&(peptideparquet["rank"]==1)].reset_index(drop=True)

                    #rename columns
                    peptideparquet.rename(columns={"sample_name":"R.FileName",
                                                "stripped_peptide":"PEP.StrippedSequence",
                                                "precursor_mz":"FG.PrecMz",
                                                "charge":"FG.Charge",
                                                "ppm_error":"FG.CalibratedMassAccuracy (PPM)",
                                                "rt":"EG.ApexRT",
                                                "ook0":"EG.IonMobility",
                                                "precursor_intensity":"FG.MS2Quantity"
                                                },inplace=True)

                    #drop columns
                    peptideparquet.drop(columns=["index","processing_run_id","ms2_id","rank","leading_aa","trailing_aa","precursor_mh",
                                                "calc_mh","denovo_tag_length","found_in_dbsearch","denovo_matches_db",
                                                "protein_group_parent_loc","protein_group_parent_list_loc","protein_group_parent_list_id"
                                                ],inplace=True,errors='ignore')
                    #fill NaN in the protein group column with -1
                    peptideparquet["protein_group_parent_id"]=peptideparquet["protein_group_parent_id"].fillna(-1)

                    #pull protein and gene info from protein parquet file and add to df 
                    protein_name=[]
                    protein_accession=[]
                    gene_id=[]
                    uncategorized_placeholder="uncat"

                    for i in range(len(peptideparquet["protein_group_parent_id"])):
                        if peptideparquet["protein_group_parent_id"][i]==-1:
                            protein_name.append(uncategorized_placeholder)
                            protein_accession.append(uncategorized_placeholder)
                            gene_id.append(uncategorized_placeholder)
                        else:
                            protein_name.append(proteinparquet["protein_name"].iloc[int(peptideparquet["protein_group_parent_id"][i])])
                            protein_accession.append(proteinparquet["protein_accession"].iloc[int(peptideparquet["protein_group_parent_id"][i])])
                            gene_id.append(proteinparquet["gene_id"].iloc[int(peptideparquet["protein_group_parent_id"][i])])

                    peptideparquet["PG.ProteinGroups"]=protein_name
                    peptideparquet["PG.ProteinAccessions"]=protein_accession
                    peptideparquet["PG.Genes"]=gene_id
                    peptideparquet=peptideparquet.drop(columns=["protein_group_parent_id"])

                    searchoutput=pd.concat([searchoutput,peptideparquet],ignore_index=True)

                #rename PTMs
                searchoutput["ptms"]=searchoutput["ptms"].astype(str)
                searchoutput["ptms"]=searchoutput["ptms"].replace({"57.0215":"Carbamidomethyl (C)",
                                                                    "15.994915":"Oxidation (M)",
                                                                    "15.9949":"Oxidation (M)",
                                                                    "79.966331":"Phospho (STY)",
                                                                    "0.984":"Deamidation (NQ)",
                                                                    },regex=True)
                searchoutput["ptm_locations"]=searchoutput["ptm_locations"].astype(str)
                searchoutput["ptm_locations"]=searchoutput["ptm_locations"].str.replace("[]","[-1]").str.replace("[","").str.replace("]","")

                #build and add the EG.ModifiedPeptide column
                modifiedpeptides=[]
                for i,entry in enumerate(searchoutput["ptm_locations"]):
                    if entry=="-1":
                        modifiedpeptides.append(searchoutput["PEP.StrippedSequence"][i])
                    else:
                        str_to_list=list(searchoutput["PEP.StrippedSequence"][i])
                        if len(searchoutput["ptm_locations"][i])==1:
                            mod_loc=int(searchoutput["ptm_locations"][i])+1
                            mod_add=searchoutput["ptms"][i]
                            str_to_list.insert(mod_loc,mod_add)
                            modifiedpeptides.append("".join(str_to_list))
                        #if theres >1 ptm, we need to reformat some strings so we can insert them in the sequence
                        else:
                            ptmlocs=searchoutput["ptm_locations"][i].strip().split(" ")
                            ptms=searchoutput["ptms"][i].replace("[","").replace("]","").replace(") ","),").split(",")
                            for ele in ptmlocs:
                                if ele=="":
                                    ptmlocs.remove(ele)
                            ptms_for_loop=[]
                            for ele in ptms:
                                ptms_for_loop.append("["+ele+"]")
                            for j,loc in enumerate(ptmlocs):
                                mod_loc=int(loc)+j+1
                                mod_add=ptms_for_loop[j]
                                str_to_list.insert(mod_loc,mod_add)
                            modifiedpeptides.append("".join(str_to_list))
                searchoutput["EG.ModifiedPeptide"]=modifiedpeptides
                searchoutput=searchoutput.drop(columns=["ptms","ptm_locations"])

                searchoutput.insert(1,"R.Condition","")
                searchoutput.insert(2,"R.Replicate","")

                #change the cwd back to the code file since we changed it to the uploaded file 
                os.chdir(os.path.dirname(os.path.realpath(__file__)))

        #for DIA-NN 2.0 input
        if ".parquet" in input.compare_searchreport1()[0]["name"]:
            if len(input.compare_searchreport1())>1:
                searchoutput=pd.DataFrame()
                for i in range(len(input.compare_searchreport1())):
                    run=pd.read_parquet(input.compare_searchreport1()[i]["datapath"])
                    searchoutput=pd.concat([searchoutput,run])
            else:
                searchoutput=pd.read_parquet(input.compare_searchreport1()[0]["datapath"])
            if input.compare_software1()=="diann2.0":
                searchoutput.rename(columns={"Run":"R.FileName"},inplace=True)
                searchoutput.insert(1,"R.Condition","")
                searchoutput.insert(2,"R.Replicate","")
                searchoutput["EG.PeakWidth"]=searchoutput["RT.Stop"]-searchoutput["RT.Start"]

                searchoutput.rename(columns={"Modified.Sequence":"EG.ModifiedPeptide",
                                            "Stripped.Sequence":"PEP.StrippedSequence",
                                            "Precursor.Charge":"FG.Charge",
                                            "Precursor.Mz":"FG.PrecMz",
                                            "Protein.Group":"PG.ProteinGroups",
                                            "Protein.Names":"PG.ProteinNames",
                                            "Genes":"PG.Genes",
                                            "RT":"EG.ApexRT",
                                            "IM":"EG.IonMobility",
                                            "Precursor.Quantity":"FG.MS2Quantity",
                                            },inplace=True)

                searchoutput.drop(columns=["Run.Index","Channel","Precursor.Id","Precursor.Lib.Index","Decoy",
                                        "Proteotypic","Protein.Ids","iRT","Predicted.RT","Predicted.iRT",
                                        "iIM","Predicted.IM","Predicted.iIM","Precursor.Normalised",
                                        "Ms1.Area","Ms1.Normalised","Ms1.Apex.Area","Ms1.Apex.Mz.Delta",
                                        "Normalisation.Factor","Quantity.Quality","Empirical.Quality",
                                        "Normalisation.Noise","Ms1.Profile.Corr","Evidence","Mass.Evidence",
                                        "Channel.Evidence","Ms1.Total.Signal.Before","Ms1.Total.Signal.After",
                                        "RT.Start","RT.Stop","FWHM","PG.TopN","PG.MaxLFQ","Genes.TopN",
                                        "Genes.MaxLFQ","Genes.MaxLFQ.Unique","PG.MaxLFQ.Quality",
                                        "Genes.MaxLFQ.Quality","Genes.MaxLFQ.Unique.Quality","Q.Value",
                                        "PEP","Global.Q.Value","Lib.Q.Value","Peptidoform.Q.Value",
                                        "Global.Peptidoform.Q.Value","Lib.Peptidoform.Q.Value",
                                        "PTM.Site.Confidence","Site.Occupancy.Probabilities","Protein.Sites",
                                        "Lib.PTM.Site.Confidence","Translated.Q.Value","Channel.Q.Value",
                                        "PG.Q.Value","PG.PEP","GG.Q.Value","Lib.PG.Q.Value"
                                        ],inplace=True,errors="ignore")
                    
                searchoutput["EG.ModifiedPeptide"]=searchoutput["EG.ModifiedPeptide"].str.replace("(","[")
                searchoutput["EG.ModifiedPeptide"]=searchoutput["EG.ModifiedPeptide"].str.replace(")","]")
                searchoutput["EG.ModifiedPeptide"]=searchoutput["EG.ModifiedPeptide"].replace({
                        "UniMod:1":"Acetyl (Protein N-term)",
                        "UniMod:4":"Carbamidomethyl (C)",
                        "UniMod:21":"Phospho (STY)",
                        "UniMod:35":"Oxidation (M)"},regex=True)

        #this line is needed for some files since some will order the search report by file name and others won't. Need to account for this
        file1=searchoutput.sort_values('R.FileName')

        return file1

    #import second search report file
    @reactive.calc
    def compare_inputfile2():
        if input.compare_searchreport2() is None:
            return pd.DataFrame()
        if ".tsv" in input.compare_searchreport2()[0]["name"]:
            if len(input.compare_searchreport2())>1:
                searchoutput=pd.DataFrame()
                for i in range(len(input.compare_searchreport2())):
                    run=pd.read_csv(input.compare_searchreport2()[i]["datapath"],sep="\t")
                    searchoutput=pd.concat([searchoutput,run])
            else:
                searchoutput=pd.read_csv(input.compare_searchreport2()[0]["datapath"],sep="\t")
            if input.compare_software2()=="diann":
                searchoutput.rename(columns={"Run":"R.FileName"},inplace=True)
                searchoutput.insert(1,"R.Condition","")
                searchoutput.insert(2,"R.Replicate","")
                searchoutput["EG.PeakWidth"]=searchoutput["RT.Stop"]-searchoutput["RT.Start"]

                searchoutput.drop(columns=["File.Name","PG.Normalized","PG.MaxLFQ","Genes.Quantity",
                                            "Genes.Normalised","Genes.MaxLFQ","Genes.MaxLFQ.Unique","Precursor.Id",
                                            "PEP","Global.Q.Value","GG.Q.Value",#"Protein.Q.Value","Global.PG.Q.Value",
                                            "Translated.Q.Value","Precursor.Translated","Translated.Quality","Ms1.Translated",
                                            "Quantity.Quality","RT.Stop","RT.Start","iRT","Predicted.iRT",
                                            "First.Protein.Description","Lib.Q.Value","Lib.PG.Q.Value","Ms1.Profile.Corr",
                                            "Ms1.Area","Evidence","Spectrum.Similarity","Averagine","Mass.Evidence",
                                            "Decoy.Evidence","Decoy.CScore","Fragment.Quant.Raw","Fragment.Quant.Corrected",
                                            "Fragment.Correlations","MS2.Scan","iIM","Predicted.IM",
                                            "Predicted.iIM","PG.Normalised","PTM.Informative","PTM.Specific","PTM.Localising",
                                            "PTM.Q.Value","PTM.Site.Confidence","Lib.PTM.Site.Confidence"],inplace=True,errors='ignore')

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
                        "UniMod:7":"Deamidation (NQ)",
                        "UniMod:21":"Phospho (STY)",
                        "UniMod:35":"Oxidation (M)"},regex=True)
            if input.compare_software2()=="ddalibrary":
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
            if input.compare_software2()=="fragpipe":
                searchoutput.rename(columns={"Spectrum File":"R.FileName"},inplace=True)
                searchoutput.insert(1,"R.Condition","")
                searchoutput.insert(2,"R.Replicate","")
                
                searchoutput["FG.CalibratedMassAccuracy (PPM)"]=(searchoutput["Delta Mass"]/searchoutput["Calculated M/Z"])*10E6

                searchoutput.drop(columns=["Spectrum","Extended Peptide","Prev AA","Next AA","Peptide Length",
                                        "Observed Mass","Calibrated Observed Mass","Calibrated Observed M/Z",
                                        "Calculated Peptide Mass","Calculated M/Z","Delta Mass",
                                        "Expectation","Hyperscore","Nextscore",
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
                    "43":"Acetyl (Protein N-term)",
                    "111":""},regex=True)

                peps=searchoutput["PEP.StrippedSequence"].tolist()
                modpeps=searchoutput["EG.ModifiedPeptide"].tolist()
                for i in range(len(peps)):
                    if type(modpeps[i])!=str:
                        modpeps[i]=peps[i]
                    else:
                        modpeps[i]=modpeps[i]
                searchoutput["EG.ModifiedPeptide"]=modpeps
            if input.compare_software2()=="fragpipe_glyco":
                #if the Spectrum File column is just a single value, get the file names from the Spectrum column
                if searchoutput["Spectrum"][0].split(".")[0] not in searchoutput["Spectrum File"][0]:
                    fragger_filelist=searchoutput["Spectrum"].str.split(".",expand=True).drop(columns=[1,2,3]).drop_duplicates().reset_index(drop=True)
                    fragger_filelist.rename(columns={0:"R.FileName"},inplace=True)

                    filenamelist=[]
                    for run in fragger_filelist["R.FileName"]:
                        fileindex=fragger_filelist[fragger_filelist["R.FileName"]==run].index.values[0]
                        filenamelist.append([fragger_filelist["R.FileName"][fileindex]]*len(searchoutput[searchoutput["Spectrum"].str.contains(run)]))

                    searchoutput.insert(0,"R.FileName",list(itertools.chain(*filenamelist)))
                    searchoutput.drop(columns=["Spectrum File"],inplace=True)

                else:
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
        
        #for BPS input
        if ".zip" in input.compare_searchreport2()[0]["name"]:
            if input.compare_software2()=="bps_timsrescore":
                searchoutput=pd.DataFrame()

                bpszip=ZipFile(input.compare_searchreport2()[0]["datapath"])
                bpszip.extractall()
                metadata_bps=pd.read_csv("metadata.csv")
                runlist=metadata_bps["processing_run_uuid"].tolist()
                cwd=os.getcwd()+"\\processing-run"
                os.chdir(cwd)

                peptide_dict=dict()
                samplename_list=[]
                for run in runlist:
                    os.chdir(cwd)
                    os.chdir(cwd+"\\"+run)

                    pgfdr_peptide=pd.read_parquet("pgfdr.peptide.parquet")                    
                    peptide_dict[run]=pgfdr_peptide

                #filter, rename/remove columns, and generate ProteinGroups and ProteinNames columns from protein_list column
                for key in peptide_dict.keys():
                    df=peptide_dict[key][peptide_dict[key]["protein_list"].str.contains("Reverse")==False].reset_index(drop=True)
                    df=df.rename(columns={"sample_name":"R.FileName",
                                    "stripped_peptide":"PEP.StrippedSequence",
                                    "precursor_mz":"FG.PrecMz",
                                    "rt":"EG.ApexRT",
                                    "charge":"FG.Charge",
                                    "ook0":"EG.IonMobility",
                                    "ppm_error":"FG.CalibratedMassAccuracy (PPM)"})

                    proteingroups=[]
                    proteinnames=[]
                    proteinlist_column=df["protein_list"].tolist()
                    for item in proteinlist_column:
                        if item.count(";")==0:
                            templist=item.split("|")
                            proteingroups.append(templist[1])
                            proteinnames.append(templist[2])
                        else:
                            proteingroups_torejoin=[]
                            proteinnames_torejoin=[]
                            for entry in item.split(";"):
                                templist=entry.split("|")
                                proteingroups_torejoin.append(templist[1])
                                proteinnames_torejoin.append(templist[2])
                            proteingroups.append(";".join(proteingroups_torejoin))
                            proteinnames.append(";".join(proteinnames_torejoin))
                    df["PG.ProteinGroups"]=proteingroups
                    df["PG.ProteinNames"]=proteinnames
                    
                    #adding a q-value filter before dropping the column
                    df=df[df["global_peptide_qvalue"]<=0.01]

                    df=df.drop(columns=["index","processing_run_uuid","ms2_id","candidate_id","protein_group_parent_id",
                                    "protein_group_name","leading_aa","trailing_aa","mokapot_psm_score","mokapot_psm_qvalue",
                                    "mokapot_psm_pep","mokapot_peptide_qvalue","mokapot_peptide_pep","global_peptide_score",
                                    "x_corr_score","delta_cn_score","precursor_mh","calc_mh","protein_list","is_contaminant",
                                    "is_target","number_matched_ions","global_peptide_qvalue"],errors='ignore')
                    
                    searchoutput=pd.concat([searchoutput,df],ignore_index=True)

                #rename ptms 
                searchoutput=searchoutput.reset_index(drop=True)
                searchoutput["ptms"]=searchoutput["ptms"].astype(str)
                searchoutput["ptms"]=searchoutput["ptms"].replace({
                        "42.010565":"Acetyl (Protein N-term)",
                        "57.021464":"Carbamidomethyl (C)",
                        "79.966331":"Phospho (STY)",
                        "15.994915":"Oxidation (M)"},regex=True)

                searchoutput["ptm_locations"]=searchoutput["ptm_locations"].astype(str)
                searchoutput["ptm_locations"]=searchoutput["ptm_locations"].str.replace("[]","-1").str.replace("[","").str.replace("]","")

                #build and add the EG.ModifiedPeptide column
                modifiedpeptides=[]
                for i,entry in enumerate(searchoutput["ptm_locations"]):
                    if entry=="-1":
                        modifiedpeptides.append(searchoutput["PEP.StrippedSequence"][i])
                    else:
                        str_to_list=list(searchoutput["PEP.StrippedSequence"][i])
                        if len(searchoutput["ptm_locations"][i])==1:
                            mod_loc=int(searchoutput["ptm_locations"][i])+1
                            mod_add=searchoutput["ptms"][i]
                            str_to_list.insert(mod_loc,mod_add)
                            modifiedpeptides.append("".join(str_to_list))
                        #if theres >1 ptm, we need to reformat some strings so we can insert them in the sequence
                        else:
                            ptmlocs=searchoutput["ptm_locations"][i].strip().split(" ")
                            ptms=searchoutput["ptms"][i].replace("[","").replace("]","").replace(") ","),").split(",")
                            ptms_for_loop=[]
                            for ele in ptms:
                                ptms_for_loop.append("["+ele+"]")
                            for j,loc in enumerate(ptmlocs):
                                mod_loc=int(loc)+j+1
                                mod_add=ptms_for_loop[j]
                                str_to_list.insert(mod_loc,mod_add)
                            modifiedpeptides.append("".join(str_to_list))
                searchoutput["EG.ModifiedPeptide"]=modifiedpeptides
                searchoutput=searchoutput.drop(columns=["ptms","ptm_locations"])

                searchoutput.insert(1,"R.Condition","")
                searchoutput.insert(2,"R.Replicate","")
                
                #change the cwd back to the code file since we changed it to the uploaded file 
                os.chdir(os.path.dirname(os.path.realpath(__file__)))
            if input.compare_software2()=="bps_timsdiann":
                searchoutput=pd.DataFrame()

                bpszip=ZipFile(input.compare_searchreport2()[0]["datapath"])
                bpszip.extractall()
                metadata_bps=pd.read_csv("metadata.csv")
                runlist=metadata_bps["processing_run_uuid"].tolist()
                cwd=os.getcwd()+"\\processing-run"
                os.chdir(cwd)

                for run in runlist:
                    os.chdir(cwd)
                    os.chdir(os.getcwd()+"\\"+run)
                    bps_resultzip=ZipFile("tims-diann.result.zip")
                    bps_resultzip.extractall()
                    results=pd.read_csv("results.tsv",sep="\t")
                    searchoutput=pd.concat([searchoutput,results])

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
                                        "Precursor.Calibrated.Mz","Fragment.Info","Fragment.Calibrated.Mz","Lib.1/K0",
                                        "Precursor.Normalised"],inplace=True,errors='ignore')

                searchoutput.rename(columns={"File.Name":"R.FileName",
                                            "Protein.Group":"PG.ProteinGroups",
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

                searchoutput.insert(1,"R.Condition","")
                searchoutput.insert(2,"R.Replicate","")
                
                #change the cwd back to the code file since we changed it to the uploaded file 
                os.chdir(os.path.dirname(os.path.realpath(__file__)))
            if input.compare_software2()=="bps_denovo":
                denovo_score=65.0

                searchoutput=pd.DataFrame()

                bpszip=ZipFile(input.compare_searchreport2()[0]["datapath"])
                bpszip.extractall()
                metadata_bps=pd.read_csv("metadata.csv")
                runlist=metadata_bps["processing_run_uuid"].tolist()
                cwd=os.getcwd()+"\\processing-run"
                os.chdir(cwd)

                peptide_dict=dict()
                protein_dict=dict()
                for run in runlist:
                    os.chdir(cwd)
                    #change working dir to next processing run subfolder
                    os.chdir(cwd+"\\"+run)

                    peptide_dict[run]=pd.read_parquet("novor-fasta-mapping-results.peptide.parquet")
                    protein_dict[run]=pd.read_parquet("novor-fasta-mapping-results.protein.parquet")

                for key in peptide_dict.keys():
                    peptideparquet=peptide_dict[key]
                    proteinparquet=protein_dict[key]

                    #filter parquet file
                    peptideparquet=peptideparquet[(peptideparquet["denovo_score"]>=denovo_score)&(peptideparquet["rank"]==1)].reset_index(drop=True)

                    #rename columns
                    peptideparquet.rename(columns={"sample_name":"R.FileName",
                                                "stripped_peptide":"PEP.StrippedSequence",
                                                "precursor_mz":"FG.PrecMz",
                                                "charge":"FG.Charge",
                                                "ppm_error":"FG.CalibratedMassAccuracy (PPM)",
                                                "rt":"EG.ApexRT",
                                                "ook0":"EG.IonMobility",
                                                "precursor_intensity":"FG.MS2Quantity"
                                                },inplace=True)

                    #drop columns
                    peptideparquet.drop(columns=["index","processing_run_id","ms2_id","rank","leading_aa","trailing_aa","precursor_mh",
                                                "calc_mh","denovo_tag_length","found_in_dbsearch","denovo_matches_db",
                                                "protein_group_parent_loc","protein_group_parent_list_loc","protein_group_parent_list_id"
                                                ],inplace=True,errors='ignore')
                    #fill NaN in the protein group column with -1
                    peptideparquet["protein_group_parent_id"]=peptideparquet["protein_group_parent_id"].fillna(-1)

                    #pull protein and gene info from protein parquet file and add to df 
                    protein_name=[]
                    protein_accession=[]
                    gene_id=[]
                    uncategorized_placeholder="uncat"

                    for i in range(len(peptideparquet["protein_group_parent_id"])):
                        if peptideparquet["protein_group_parent_id"][i]==-1:
                            protein_name.append(uncategorized_placeholder)
                            protein_accession.append(uncategorized_placeholder)
                            gene_id.append(uncategorized_placeholder)
                        else:
                            protein_name.append(proteinparquet["protein_name"].iloc[int(peptideparquet["protein_group_parent_id"][i])])
                            protein_accession.append(proteinparquet["protein_accession"].iloc[int(peptideparquet["protein_group_parent_id"][i])])
                            gene_id.append(proteinparquet["gene_id"].iloc[int(peptideparquet["protein_group_parent_id"][i])])

                    peptideparquet["PG.ProteinGroups"]=protein_name
                    peptideparquet["PG.ProteinAccessions"]=protein_accession
                    peptideparquet["PG.Genes"]=gene_id
                    peptideparquet=peptideparquet.drop(columns=["protein_group_parent_id"])

                    searchoutput=pd.concat([searchoutput,peptideparquet],ignore_index=True)

                #rename PTMs
                searchoutput["ptms"]=searchoutput["ptms"].astype(str)
                searchoutput["ptms"]=searchoutput["ptms"].replace({"57.0215":"Carbamidomethyl (C)",
                                                                    "15.994915":"Oxidation (M)",
                                                                    "15.9949":"Oxidation (M)",
                                                                    "79.966331":"Phospho (STY)",
                                                                    "0.984":"Deamidation (NQ)",
                                                                    },regex=True)
                searchoutput["ptm_locations"]=searchoutput["ptm_locations"].astype(str)
                searchoutput["ptm_locations"]=searchoutput["ptm_locations"].str.replace("[]","[-1]").str.replace("[","").str.replace("]","")

                #build and add the EG.ModifiedPeptide column
                modifiedpeptides=[]
                for i,entry in enumerate(searchoutput["ptm_locations"]):
                    if entry=="-1":
                        modifiedpeptides.append(searchoutput["PEP.StrippedSequence"][i])
                    else:
                        str_to_list=list(searchoutput["PEP.StrippedSequence"][i])
                        if len(searchoutput["ptm_locations"][i])==1:
                            mod_loc=int(searchoutput["ptm_locations"][i])+1
                            mod_add=searchoutput["ptms"][i]
                            str_to_list.insert(mod_loc,mod_add)
                            modifiedpeptides.append("".join(str_to_list))
                        #if theres >1 ptm, we need to reformat some strings so we can insert them in the sequence
                        else:
                            ptmlocs=searchoutput["ptm_locations"][i].strip().split(" ")
                            ptms=searchoutput["ptms"][i].replace("[","").replace("]","").replace(") ","),").split(",")
                            for ele in ptmlocs:
                                if ele=="":
                                    ptmlocs.remove(ele)
                            ptms_for_loop=[]
                            for ele in ptms:
                                ptms_for_loop.append("["+ele+"]")
                            for j,loc in enumerate(ptmlocs):
                                mod_loc=int(loc)+j+1
                                mod_add=ptms_for_loop[j]
                                str_to_list.insert(mod_loc,mod_add)
                            modifiedpeptides.append("".join(str_to_list))
                searchoutput["EG.ModifiedPeptide"]=modifiedpeptides
                searchoutput=searchoutput.drop(columns=["ptms","ptm_locations"])

                searchoutput.insert(1,"R.Condition","")
                searchoutput.insert(2,"R.Replicate","")

                #change the cwd back to the code file since we changed it to the uploaded file 
                os.chdir(os.path.dirname(os.path.realpath(__file__)))

        #for DIA-NN 2.0 input
        if ".parquet" in input.compare_searchreport2()[0]["name"]:
            if len(input.compare_searchreport2())>1:
                searchoutput=pd.DataFrame()
                for i in range(len(input.compare_searchreport2())):
                    run=pd.read_parquet(input.compare_searchreport2()[i]["datapath"])
                    searchoutput=pd.concat([searchoutput,run])
            else:
                searchoutput=pd.read_parquet(input.compare_searchreport2()[0]["datapath"])
            if input.compare_software2()=="diann2.0":
                searchoutput.rename(columns={"Run":"R.FileName"},inplace=True)
                searchoutput.insert(1,"R.Condition","")
                searchoutput.insert(2,"R.Replicate","")
                searchoutput["EG.PeakWidth"]=searchoutput["RT.Stop"]-searchoutput["RT.Start"]

                searchoutput.rename(columns={"Modified.Sequence":"EG.ModifiedPeptide",
                                            "Stripped.Sequence":"PEP.StrippedSequence",
                                            "Precursor.Charge":"FG.Charge",
                                            "Precursor.Mz":"FG.PrecMz",
                                            "Protein.Group":"PG.ProteinGroups",
                                            "Protein.Names":"PG.ProteinNames",
                                            "Genes":"PG.Genes",
                                            "RT":"EG.ApexRT",
                                            "IM":"EG.IonMobility",
                                            "Precursor.Quantity":"FG.MS2Quantity",
                                            },inplace=True)

                searchoutput.drop(columns=["Run.Index","Channel","Precursor.Id","Precursor.Lib.Index","Decoy",
                                        "Proteotypic","Protein.Ids","iRT","Predicted.RT","Predicted.iRT",
                                        "iIM","Predicted.IM","Predicted.iIM","Precursor.Normalised",
                                        "Ms1.Area","Ms1.Normalised","Ms1.Apex.Area","Ms1.Apex.Mz.Delta",
                                        "Normalisation.Factor","Quantity.Quality","Empirical.Quality",
                                        "Normalisation.Noise","Ms1.Profile.Corr","Evidence","Mass.Evidence",
                                        "Channel.Evidence","Ms1.Total.Signal.Before","Ms1.Total.Signal.After",
                                        "RT.Start","RT.Stop","FWHM","PG.TopN","PG.MaxLFQ","Genes.TopN",
                                        "Genes.MaxLFQ","Genes.MaxLFQ.Unique","PG.MaxLFQ.Quality",
                                        "Genes.MaxLFQ.Quality","Genes.MaxLFQ.Unique.Quality","Q.Value",
                                        "PEP","Global.Q.Value","Lib.Q.Value","Peptidoform.Q.Value",
                                        "Global.Peptidoform.Q.Value","Lib.Peptidoform.Q.Value",
                                        "PTM.Site.Confidence","Site.Occupancy.Probabilities","Protein.Sites",
                                        "Lib.PTM.Site.Confidence","Translated.Q.Value","Channel.Q.Value",
                                        "PG.Q.Value","PG.PEP","GG.Q.Value","Lib.PG.Q.Value"
                                        ],inplace=True,errors="ignore")
                    
                searchoutput["EG.ModifiedPeptide"]=searchoutput["EG.ModifiedPeptide"].str.replace("(","[")
                searchoutput["EG.ModifiedPeptide"]=searchoutput["EG.ModifiedPeptide"].str.replace(")","]")
                searchoutput["EG.ModifiedPeptide"]=searchoutput["EG.ModifiedPeptide"].replace({
                        "UniMod:1":"Acetyl (Protein N-term)",
                        "UniMod:4":"Carbamidomethyl (C)",
                        "UniMod:21":"Phospho (STY)",
                        "UniMod:35":"Oxidation (M)"},regex=True)

        #this line is needed for some files since some will order the search report by file name and others won't. Need to account for this
        file2=searchoutput.sort_values('R.FileName')

        return file2

    #upload filled metadata table
    @reactive.calc
    def compare_inputmetadata():
        if input.compare_metadata_upload() is None:
            metadata=pd.DataFrame(columns=["R.FileName1","R.FileName2","R.Condition","R.Replicate","remove"])
            return metadata
        else:
            metadata=pd.read_csv(input.compare_metadata_upload()[0]["datapath"],sep=",")
            return metadata

    #render metadata table
    @render.data_frame
    def compare_metadata_table():
        if input.compare_use_uploaded_metadata()==True:
            metadata=compare_inputmetadata()
            if input.compare_metadata_upload() is None:
                metadata=pd.DataFrame(columns=["R.FileName1","R.FileName2","R.Condition","R.Replicate","remove"])
            metadata=metadata.drop(columns=["order","Concentration"])
            return render.DataGrid(metadata,editable=True)
        else:
            if input.compare_searchreport1() is not None and input.compare_searchreport2() is not None:
                file1=compare_inputfile1()
                file2=compare_inputfile2()
                metadata=pd.DataFrame(columns=["R.FileName1","R.FileName2","R.Condition","R.Replicate","remove"])
                metadata["R.FileName1"]=file1["R.FileName"].drop_duplicates().reset_index(drop=True)
                metadata["R.FileName2"]=file2["R.FileName"].drop_duplicates().reset_index(drop=True)
                return render.DataGrid(metadata,editable=True)
            else:
                metadata=pd.DataFrame(columns=["R.FileName1","R.FileName2","R.Condition","R.Replicate","remove"])
                return render.DataGrid(metadata,editable=True)
    
    #render metadata condition table
    @render.data_frame
    def compare_metadata_condition_table():
        if input.compare_use_uploaded_metadata()==True:
            metadata=compare_inputmetadata()
            if metadata is None:
                metadata_condition=pd.DataFrame(columns=["R.Condition","order","Concentration"])
            if input.compare_remove()==True:
                metadata=metadata[metadata.remove !="x"]
            metadata_condition=pd.DataFrame()
            metadata_condition["R.Condition"]=metadata["R.Condition"].drop_duplicates()
            metadata_condition["order"]=metadata["order"].drop_duplicates()
            metadata_condition["Concentration"]=metadata["Concentration"].drop_duplicates()
            return render.DataGrid(metadata_condition,editable=True)
        else:
            metadata=compare_metadata_table.data_view()
            if input.compare_searchreport1() is not None and input.compare_searchreport2() is not None:
                if input.compare_remove()==True:
                    metadata=metadata[metadata.remove !="x"]
                metadata_condition=pd.DataFrame(metadata[["R.Condition"]]).drop_duplicates().reset_index(drop=True)
                metadata_condition["order"]=metadata_condition.apply(lambda _: '', axis=1)
                metadata_condition["Concentration"]=metadata_condition.apply(lambda _: '', axis=1)
                return render.DataGrid(metadata_condition,editable=True)
            else:
                metadata_condition=pd.DataFrame(columns=["R.Condition","order","Concentration"])
                return render.DataGrid(metadata_condition,editable=True)
    
    #download metadata table shown
    @render.download(filename="metadata_"+str(date.today())+".csv")
    def compare_metadata_download():
        metadata=compare_metadata_table.data_view()
        metadata_condition=compare_metadata_condition_table.data_view()

        orderlist=[]
        concentrationlist=[]
        metadata_fordownload=pd.DataFrame()
        for run in metadata_condition["R.Condition"]:
            fileindex=metadata_condition[metadata_condition["R.Condition"]==run].index.values[0]
            orderlist.append([metadata_condition["order"][fileindex]]*len(metadata[metadata["R.Condition"]==run]))
            concentrationlist.append([metadata_condition["Concentration"][fileindex]]*len(metadata[metadata["R.Condition"]==run]))
        metadata_fordownload["R.FileName1"]=metadata["R.FileName1"]
        metadata_fordownload["R.FileName2"]=metadata["R.FileName2"]
        metadata_fordownload["R.Condition"]=metadata["R.Condition"]
        metadata_fordownload["R.Replicate"]=metadata["R.Replicate"]
        metadata_fordownload["remove"]=metadata["remove"]
        metadata_fordownload["order"]=list(itertools.chain(*orderlist))
        metadata_fordownload["Concentration"]=list(itertools.chain(*concentrationlist))
        with io.BytesIO() as buf:
            metadata_fordownload.to_csv(buf,index=False)
            yield buf.getvalue()

    #update search files based on metadata
    @reactive.calc
    @reactive.event(input.compare_rerun_metadata,ignore_none=False)
    def compare_metadata_update():
        file1=compare_inputfile1()
        file2=compare_inputfile2()
        metadata=compare_metadata_table.data_view()
        metadata_condition=compare_metadata_condition_table.data_view()

        RConditionlist1=[]
        RReplicatelist1=[]
        for run in file1["R.FileName"].drop_duplicates().tolist():
            fileindex=metadata[metadata["R.FileName1"]==run].index.values[0]
            RConditionlist1.append([metadata["R.Condition"][fileindex]]*len(file1.set_index("R.FileName").loc[run]))
            RReplicatelist1.append([metadata["R.Replicate"][fileindex]]*len(file1.set_index("R.FileName").loc[run]))
        file1["R.Condition"]=list(itertools.chain(*RConditionlist1))
        file1["R.Replicate"]=list(itertools.chain(*RReplicatelist1))
        file1["R.Replicate"]=file1["R.Replicate"].astype(int)

        RConditionlist2=[]
        RReplicatelist2=[]
        for run in file2["R.FileName"].drop_duplicates().tolist():
            fileindex=metadata[metadata["R.FileName2"]==run].index.values[0]
            RConditionlist2.append([metadata["R.Condition"][fileindex]]*len(file2.set_index("R.FileName").loc[run]))
            RReplicatelist2.append([metadata["R.Replicate"][fileindex]]*len(file2.set_index("R.FileName").loc[run]))
        file2["R.Condition"]=list(itertools.chain(*RConditionlist2))
        file2["R.Replicate"]=list(itertools.chain(*RReplicatelist2))
        file2["R.Replicate"]=file2["R.Replicate"].astype(int)

        if input.compare_remove()==True:
            editedmetadata=metadata[metadata.remove !="x"]
            file1=file1.set_index("R.FileName").loc[editedmetadata["R.FileName1"].tolist()].reset_index()
            file2=file2.set_index("R.FileName").loc[editedmetadata["R.FileName2"].tolist()].reset_index()
        
        if input.compare_reorder()==True:
            metadata_condition["order"]=metadata_condition["order"].astype(int)
            sortedmetadata_bycondition=metadata_condition.sort_values(by="order").reset_index(drop=True)
            file1=file1.set_index("R.Condition").loc[sortedmetadata_bycondition["R.Condition"].tolist()].reset_index()
            file2=file2.set_index("R.Condition").loc[sortedmetadata_bycondition["R.Condition"].tolist()].reset_index()
        
        if input.compare_concentration()==True:
            concentrationlist=[]

        return file1,file2

    #generate necessary dfs for plotting IDs
    @reactive.calc
    def compare_variables_dfs():
        file1,file2=compare_metadata_update()

        file1["R.Condition"]=file1["R.Condition"].apply(str)
        if "Cond_Rep" not in file1.columns:
            file1.insert(0,"Cond_Rep",file1["R.Condition"]+"_"+file1["R.Replicate"].apply(str))
        elif "Cond_Rep" in file1.columns:
            file1["Cond_Rep"]=file1["R.Condition"]+"_"+file1["R.Replicate"].apply(str)
        resultdf1=pd.DataFrame(file1[["Cond_Rep","R.FileName","R.Condition","R.Replicate"]].drop_duplicates()).reset_index(drop=True)
        sampleconditions=file1["R.Condition"].drop_duplicates().tolist()
        maxreplicatelist=[]
        for i in sampleconditions:
            samplegroup=pd.DataFrame(file1[file1["R.Condition"]==i])
            maxreplicates=max(file1["R.Replicate"].tolist())
            maxreplicatelist.append(maxreplicates)
        averagedf1=pd.DataFrame({"R.Condition":sampleconditions,"N.Replicates":maxreplicatelist})

        file2["R.Condition"]=file2["R.Condition"].apply(str)
        if "Cond_Rep" not in file2.columns:
            file2.insert(0,"Cond_Rep",file2["R.Condition"]+"_"+file2["R.Replicate"].apply(str))
        elif "Cond_Rep" in file2.columns:
            file2["Cond_Rep"]=file2["R.Condition"]+"_"+file2["R.Replicate"].apply(str)
        resultdf2=pd.DataFrame(file2[["Cond_Rep","R.FileName","R.Condition","R.Replicate"]].drop_duplicates()).reset_index(drop=True)
        sampleconditions=file2["R.Condition"].drop_duplicates().tolist()
        maxreplicatelist=[]
        for i in sampleconditions:
            samplegroup=pd.DataFrame(file2[file2["R.Condition"]==i])
            maxreplicates=max(file2["R.Replicate"].tolist())
            maxreplicatelist.append(maxreplicates)
        averagedf2=pd.DataFrame({"R.Condition":sampleconditions,"N.Replicates":maxreplicatelist})

        sampleconditions=resultdf1["R.Condition"].drop_duplicates().reset_index(drop=True)

        numproteins1=[]
        numproteins2pepts1=[]
        numpeptides1=[]
        numprecursors1=[]

        for i in file1["Cond_Rep"].drop_duplicates().reset_index(drop=True):
            replicatedata=file1[file1["Cond_Rep"]==i]

            if replicatedata.empty:
                continue
            #identified proteins
            numproteins1.append(replicatedata["PG.ProteinGroups"].nunique())
            #identified proteins with 2 peptides
            numproteins2pepts1.append(len(replicatedata[["PG.ProteinGroups","EG.ModifiedPeptide"]].drop_duplicates().groupby("PG.ProteinGroups").size().reset_index(name="peptides").query("peptides>1")))
            #identified peptides
            numpeptides1.append(replicatedata["EG.ModifiedPeptide"].nunique())
            #identified precursors
            numprecursors1.append(len(replicatedata[["EG.ModifiedPeptide","FG.Charge"]].drop_duplicates()))
        resultdf1["proteins"]=numproteins1
        resultdf1["proteins2pepts"]=numproteins2pepts1
        resultdf1["peptides"]=numpeptides1
        resultdf1["precursors"]=numprecursors1

        #avg and stdev values for IDs appended to averagedf dataframe, which holds lists of all the calculated values here
        columnlist=["proteins","proteins2pepts","peptides","precursors"]
        for i in columnlist:
            avglist=[]
            stdevlist=[]
            for j in sampleconditions:
                samplecondition=resultdf1[resultdf1["R.Condition"]==j]
                avglist.append(round(np.average(samplecondition[i].to_numpy())))
                stdevlist.append(np.std(samplecondition[i].to_numpy()))
            averagedf1[i+"_avg"]=avglist
            averagedf1[i+"_stdev"]=stdevlist

        numproteins2=[]
        numproteins2pepts2=[]
        numpeptides2=[]
        numprecursors2=[]

        for i in file2["Cond_Rep"].drop_duplicates().reset_index(drop=True):
            replicatedata=file2[file2["Cond_Rep"]==i]

            if replicatedata.empty:
                continue
            #identified proteins
            numproteins2.append(replicatedata["PG.ProteinGroups"].nunique())
            #identified proteins with 2 peptides
            numproteins2pepts2.append(len(replicatedata[["PG.ProteinGroups","EG.ModifiedPeptide"]].drop_duplicates().groupby("PG.ProteinGroups").size().reset_index(name="peptides").query("peptides>1")))
            #identified peptides
            numpeptides2.append(replicatedata["EG.ModifiedPeptide"].nunique())
            #identified precursors
            numprecursors2.append(len(replicatedata[["EG.ModifiedPeptide","FG.Charge"]].drop_duplicates()))
        resultdf2["proteins"]=numproteins2
        resultdf2["proteins2pepts"]=numproteins2pepts2
        resultdf2["peptides"]=numpeptides2
        resultdf2["precursors"]=numprecursors2

        #avg and stdev values for IDs appended to averagedf dataframe, which holds lists of all the calculated values here
        columnlist=["proteins","proteins2pepts","peptides","precursors"]
        for i in columnlist:
            avglist=[]
            stdevlist=[]
            for j in sampleconditions:
                samplecondition=resultdf1[resultdf1["R.Condition"]==j]
                avglist.append(round(np.average(samplecondition[i].to_numpy())))
                stdevlist.append(np.std(samplecondition[i].to_numpy()))
            averagedf2[i+"_avg"]=avglist
            averagedf2[i+"_stdev"]=stdevlist
        return file1,file2,resultdf1,averagedf1,resultdf2,averagedf2
    
    #function for finding the PTMs in the data
    @reactive.calc
    def compare_find_ptms():
        file1,file2,resultdf1,averagedf1,resultdf2,averagedf2=compare_variables_dfs()
        peplist=file1["EG.ModifiedPeptide"]
        ptmlist=[]
        for i in peplist:
            ptmlist.append(re.findall(r"[^[]*\[([^]]*)\]",i))
        return(list(OrderedDict.fromkeys(itertools.chain(*ptmlist))))

    # ====================================== ID Counts
    #ID Counts plot
    @reactive.effect
    def _():
        @render.plot(width=input.compare_id_counts_width(),height=input.compare_id_counts_height())
        def compare_id_counts():
            file1,file2,resultdf1,averagedf1,resultdf2,averagedf2=compare_variables_dfs()
            runlist=resultdf1["Cond_Rep"]

            x=np.arange(len(runlist))
            width=0.4
            y_padding=input.ypadding()
            titlefont=input.titlefont()
            axisfont=input.axisfont()
            labelfont=input.labelfont()

            if input.compare_software1()=="spectronaut":
                label1="Spectronaut"
            if input.compare_software1()=="diann":
                label1="DIA-NN"
            if input.compare_software1()=="fragpipe":
                label1="FragPipe"
            if input.compare_software1()=="bps_timsrescore":
                label1="tims-Rescore"
            if input.compare_software1()=="bps_timsdiann":
                label1="tims-DIANN"
            if input.compare_software1()=="bps_denovo":
                label1="BPS Novor"

            if input.compare_software2()=="spectronaut":
                label2="Spectronaut"
            if input.compare_software2()=="diann":
                label2="DIA-NN"
            if input.compare_software2()=="fragpipe":
                label2="FragPipe"
            if input.compare_software2()=="bps_timsrescore":
                label2="tims-Rescore"
            if input.compare_software2()=="bps_timsdiann":
                label2="tims-DIANN"
            if input.compare_software2()=="bps_denovo":
                label2="BPS Novor"

            fig,ax=plt.subplots(nrows=2,ncols=2,sharex=True)
            ax1=ax[0,0]
            ax2=ax[0,1]
            ax3=ax[1,0]
            ax4=ax[1,1]

            ax1.bar(x,resultdf1["proteins"],width=width,label=label1)
            ax1.bar(x+width,resultdf2["proteins"],width=width,label=label2)
            ax1.bar_label(ax1.containers[0],label_type="edge",padding=5,rotation=90,fontsize=labelfont)
            ax1.bar_label(ax1.containers[1],label_type="edge",padding=5,rotation=90,fontsize=labelfont)
            maxvalue1=max([max(resultdf1["proteins"]),max(resultdf2["proteins"])])
            ax1.set_ylim(top=maxvalue1+(y_padding*maxvalue1))
            ax1.set_title("Protein Groups",fontsize=titlefont)

            ax2.bar(x,resultdf1["proteins2pepts"],width=width)
            ax2.bar(x+width,resultdf2["proteins2pepts"],width=width)
            ax2.bar_label(ax2.containers[0],label_type="edge",padding=5,rotation=90,fontsize=labelfont)
            ax2.bar_label(ax2.containers[1],label_type="edge",padding=5,rotation=90,fontsize=labelfont)
            maxvalue2=max([max(resultdf1["proteins2pepts"]),max(resultdf2["proteins2pepts"])])
            ax2.set_ylim(top=maxvalue2+(y_padding*maxvalue2))
            ax2.set_title("Protein Groups with >2 Peptides",fontsize=titlefont)

            ax3.bar(x,resultdf1["peptides"],width=width)
            ax3.bar(x+width,resultdf2["peptides"],width=width)
            ax3.bar_label(ax3.containers[0],label_type="edge",padding=5,rotation=90,fontsize=labelfont)
            ax3.bar_label(ax3.containers[1],label_type="edge",padding=5,rotation=90,fontsize=labelfont)
            maxvalue3=max([max(resultdf1["peptides"]),max(resultdf2["peptides"])])
            ax3.set_ylim(top=maxvalue3+(y_padding*maxvalue3))
            ax3.set_xlabel("Condition",fontsize=axisfont)
            ax3.set_xticks(x+width/2,runlist)
            ax3.tick_params(axis="x",labelsize=axisfont,rotation=input.xaxis_label_rotation())
            ax3.set_title("Peptides",fontsize=titlefont)

            ax4.bar(x,resultdf1["precursors"],width=width)
            ax4.bar(x+width,resultdf2["precursors"],width=width)
            ax4.bar_label(ax4.containers[0],label_type="edge",padding=5,rotation=90,fontsize=labelfont)
            ax4.bar_label(ax4.containers[1],label_type="edge",padding=5,rotation=90,fontsize=labelfont)
            maxvalue4=max([max(resultdf1["precursors"]),max(resultdf2["precursors"])])
            ax4.set_ylim(top=maxvalue4+(y_padding*maxvalue4))
            ax4.set_xlabel("Condition",fontsize=axisfont)
            ax4.set_xticks(x+width/2,runlist)
            ax4.tick_params(axis="x",labelsize=axisfont,rotation=input.xaxis_label_rotation())
            ax4.set_title("Precursors",fontsize=titlefont)

            fig.legend(loc="upper left",bbox_to_anchor=(0,1))
            fig.text(0, 0.6,"Counts",ha="left",va="center",rotation="vertical",fontsize=axisfont)

            ax1.set_axisbelow(True)
            ax1.grid(linestyle="--")
            ax2.set_axisbelow(True)
            ax2.grid(linestyle="--")
            ax3.set_axisbelow(True)
            ax3.grid(linestyle="--")
            ax4.set_axisbelow(True)
            ax4.grid(linestyle="--")

            fig.set_tight_layout(True)

    # ====================================== Venn Diagram
    @render.ui
    def compare_venn_run_ui():
        file1,file2,resultdf1,averagedf1,resultdf2,averagedf2=compare_variables_dfs()
        if input.compare_venn_conditionorrun()=="condition":
            opts=resultdf1["R.Condition"].drop_duplicates().tolist()
            return ui.input_selectize("compare_venn_run_list","Pick condition to compare",choices=opts)
        if input.compare_venn_conditionorrun()=="individual":
            opts=resultdf1["Cond_Rep"].tolist()
            return ui.input_selectize("compare_venn_run_list","Pick run to compare",choices=opts)   
    @render.ui
    def compare_venn_ptm_ui():
        if input.compare_venn_plotproperty()=="peptides" or input.compare_venn_plotproperty()=="precursors" or input.compare_venn_plotproperty()=="peptides_stripped":
            return ui.input_switch("compare_venn_ptm","Compare only for specific PTM?",value=False)
    @render.ui
    def compare_venn_ptmlist_ui():
        if input.compare_venn_plotproperty()=="peptides" or input.compare_venn_plotproperty()=="precursors" or input.compare_venn_plotproperty()=="peptides_stripped":
            if input.compare_venn_ptm()==True:
                listofptms=compare_find_ptms()
                ptmshortened=[]
                for i in range(len(listofptms)):
                    ptmshortened.append(re.sub(r'\(.*?\)',"",listofptms[i]))
                ptmdict={ptmshortened[i]: listofptms[i] for i in range(len(listofptms))}
                return ui.input_selectize("compare_venn_foundptms","Pick PTM to plot data for",choices=ptmdict,selected=listofptms[0])
    @render.ui
    def compare_venn_specific_length_ui():
        if input.compare_venn_plotproperty()=="peptides" or input.compare_venn_plotproperty()=="precursors" or input.compare_venn_plotproperty()=="peptides_stripped":
            return ui.input_switch("compare_venn_specific_length","Compare specific peptide length?",value=False,width="300px")
    @render.ui
    def compare_venn_peplength_ui():
        if input.compare_venn_specific_length()==True:
            return ui.input_slider("compare_venn_peplength_pick","Pick specific peptide length to compare:",min=3,max=30,value=9,step=1,ticks=True)
    #plot Venn Diagram
    @reactive.effect
    def _():
        @render.plot(width=input.compare_venn_width(),height=input.compare_venn_height())
        def compare_venn_plot():
            file1,file2,resultdf1,averagedf1,resultdf2,averagedf2=compare_variables_dfs()

            if input.compare_software1()=="spectronaut":
                label1="Spectronaut"
            if input.compare_software1()=="diann":
                label1="DIA-NN"
            if input.compare_software1()=="diann2.0":
                label1="DIA-NN 2.0"
            if input.compare_software1()=="fragpipe":
                label1="FragPipe"
            if input.compare_software1()=="bps_timsrescore":
                label1="tims-Rescore"
            if input.compare_software1()=="bps_timsdiann":
                label1="tims-DIANN"
            if input.compare_software1()=="bps_denovo":
                label1="BPS Novor"

            if input.compare_software2()=="spectronaut":
                label2="Spectronaut"
            if input.compare_software2()=="diann":
                label2="DIA-NN"
            if input.compare_software2()=="diann2.0":
                label2="DIA-NN 2.0"
            if input.compare_software2()=="fragpipe":
                label2="FragPipe"
            if input.compare_software2()=="bps_timsrescore":
                label2="tims-Rescore"
            if input.compare_software2()=="bps_timsdiann":
                label2="tims-DIANN"
            if input.compare_software2()=="bps_denovo":
                label2="BPS Novor"

            if input.compare_venn_conditionorrun()=="condition":
                A=file1[file1["R.Condition"]==input.compare_venn_run_list()][["PG.ProteinGroups","EG.ModifiedPeptide","FG.Charge","PEP.StrippedSequence"]].drop_duplicates().reset_index(drop=True)
                B=file2[file2["R.Condition"]==input.compare_venn_run_list()][["PG.ProteinGroups","EG.ModifiedPeptide","FG.Charge","PEP.StrippedSequence"]].drop_duplicates().reset_index(drop=True)
            if input.compare_venn_conditionorrun()=="individual":
                A=file1[file1["Cond_Rep"]==input.compare_venn_run_list()][["PG.ProteinGroups","EG.ModifiedPeptide","FG.Charge","PEP.StrippedSequence"]].drop_duplicates().reset_index(drop=True)
                B=file2[file2["Cond_Rep"]==input.compare_venn_run_list()][["PG.ProteinGroups","EG.ModifiedPeptide","FG.Charge","PEP.StrippedSequence"]].drop_duplicates().reset_index(drop=True)

            #some software return EG.ModifiedPeptide with _seq_, need to strip the underscores in order for them to be able to be compared
            A_strippedmodpeplist=[]
            B_strippedmodpeplist=[]
            for ele1 in A["EG.ModifiedPeptide"]:
                if ele1.find("_")==-1:
                    A_strippedmodpeplist.append(ele1)
                else:
                    A_strippedmodpeplist.append(ele1.split("_")[1]) 
            for ele2 in B["EG.ModifiedPeptide"]:
                if ele2.find("_")==-1:
                    B_strippedmodpeplist.append(ele2)
                else:
                    B_strippedmodpeplist.append(ele2.split("_")[1])
            A["EG.ModifiedPeptide"]=A_strippedmodpeplist
            B["EG.ModifiedPeptide"]=B_strippedmodpeplist

            A["pep_charge"]=A["EG.ModifiedPeptide"]+A["FG.Charge"].astype(str)
            B["pep_charge"]=B["EG.ModifiedPeptide"]+B["FG.Charge"].astype(str)

            A_peplength=[]
            for pep in A["PEP.StrippedSequence"]:
                A_peplength.append(len(pep))
            A["Peptide Length"]=A_peplength

            B_peplength=[]
            for pep in B["PEP.StrippedSequence"]:
                B_peplength.append(len(pep))
            B["Peptide Length"]=B_peplength

            titlemodlist=[]
            if input.compare_venn_plotproperty()=="proteingroups":
                a=set(A["PG.ProteinGroups"])
                b=set(B["PG.ProteinGroups"])
                titlemod="Protein Groups"
            if input.compare_venn_plotproperty()=="peptides":
                if input.compare_venn_ptm()==True:
                    ptm=input.compare_venn_foundptms()
                    A=A[A["EG.ModifiedPeptide"].str.contains(ptm)]
                    B=B[B["EG.ModifiedPeptide"].str.contains(ptm)]
                    titlemodlist.append(ptm.strip())
                if input.compare_venn_specific_length()==True:
                    A=A[A["Peptide Length"]==int(input.compare_venn_peplength_pick())]
                    B=B[B["Peptide Length"]==int(input.compare_venn_peplength_pick())]
                    titlemodlist.append(str(input.compare_venn_peplength_pick())+"mers")
                else:
                    A=A
                    B=B
                a=set(A["EG.ModifiedPeptide"])
                b=set(B["EG.ModifiedPeptide"])
                titlemod="Peptides"
            if input.compare_venn_plotproperty()=="precursors":
                if input.compare_venn_ptm()==True:
                    ptm=input.compare_venn_foundptms()
                    A=A[A["EG.ModifiedPeptide"].str.contains(ptm)]
                    B=B[B["EG.ModifiedPeptide"].str.contains(ptm)]
                    titlemodlist.append(ptm.strip())
                if input.compare_venn_specific_length()==True:
                    A=A[A["Peptide Length"]==int(input.compare_venn_peplength_pick())]
                    B=B[B["Peptide Length"]==int(input.compare_venn_peplength_pick())]
                    titlemodlist.append(str(input.compare_venn_peplength_pick())+"mers")
                else:
                    A=A
                    B=B
                a=set(A["pep_charge"])
                b=set(B["pep_charge"])
                titlemod="Precursors"
            if input.compare_venn_plotproperty()=="peptides_stripped":
                if input.compare_venn_ptm()==True:
                    ptm=input.compare_venn_foundptms()
                    A=A[A["EG.ModifiedPeptide"].str.contains(ptm)]
                    B=B[B["EG.ModifiedPeptide"].str.contains(ptm)]
                    titlemodlist.append(ptm.strip())
                if input.compare_venn_specific_length()==True:
                    A=A[A["Peptide Length"]==int(input.compare_venn_peplength_pick())]
                    B=B[B["Peptide Length"]==int(input.compare_venn_peplength_pick())]
                    titlemodlist.append(str(input.compare_venn_peplength_pick())+"mers")
                else:
                    A=A
                    B=B
                a=set(A["PEP.StrippedSequence"])
                b=set(B["PEP.StrippedSequence"])
                titlemod="Stripped Peptides"
            if titlemodlist==[]:
                titlemodlist=""
            else:
                titlemodlist=" ("+", ".join(titlemodlist)+")"
            fig,ax=plt.subplots()
            Ab=len(a-b)
            aB=len(b-a)
            AB=len(a&b)
            venn2(subsets=(Ab,aB,AB),set_labels=(label1,label2),set_colors=("tab:blue","tab:orange"),ax=ax)
            venn2_circles(subsets=(Ab,aB,AB),linestyle="dashed",linewidth=0.5)
            plt.title("Venn Diagram for "+input.compare_venn_run_list()+" "+titlemod+titlemodlist)
    @render.download(filename=lambda: f"VennList_A-{input.compare_software1()}_vs_B-{input.compare_software2()}_{input.compare_venn_plotproperty()}.csv")
    def compare_venn_download():
        file1,file2,resultdf1,averagedf1,resultdf2,averagedf2=compare_variables_dfs()
        if input.compare_venn_conditionorrun()=="condition":
            A=file1[file1["R.Condition"]==input.compare_venn_run_list()][["PG.ProteinGroups","EG.ModifiedPeptide","FG.Charge","PEP.StrippedSequence"]].drop_duplicates().reset_index(drop=True)
            B=file2[file2["R.Condition"]==input.compare_venn_run_list()][["PG.ProteinGroups","EG.ModifiedPeptide","FG.Charge","PEP.StrippedSequence"]].drop_duplicates().reset_index(drop=True)
        if input.compare_venn_conditionorrun()=="individual":
            A=file1[file1["Cond_Rep"]==input.compare_venn_run_list()][["PG.ProteinGroups","EG.ModifiedPeptide","FG.Charge","PEP.StrippedSequence"]].drop_duplicates().reset_index(drop=True)
            B=file2[file2["Cond_Rep"]==input.compare_venn_run_list()][["PG.ProteinGroups","EG.ModifiedPeptide","FG.Charge","PEP.StrippedSequence"]].drop_duplicates().reset_index(drop=True)

        #some software return EG.ModifiedPeptide with _seq_, need to strip the underscores in order for them to be able to be compared
        A_strippedmodpeplist=[]
        B_strippedmodpeplist=[]
        for ele1 in A["EG.ModifiedPeptide"]:
            if ele1.find("_")==-1:
                A_strippedmodpeplist.append(ele1)
            else:
                A_strippedmodpeplist.append(ele1.split("_")[1]) 
        for ele2 in B["EG.ModifiedPeptide"]:
            if ele2.find("_")==-1:
                B_strippedmodpeplist.append(ele2)
            else:
                B_strippedmodpeplist.append(ele2.split("_")[1])
        A["EG.ModifiedPeptide"]=A_strippedmodpeplist
        B["EG.ModifiedPeptide"]=B_strippedmodpeplist

        A["pep_charge"]=A["EG.ModifiedPeptide"]+A["FG.Charge"].astype(str)
        B["pep_charge"]=B["EG.ModifiedPeptide"]+B["FG.Charge"].astype(str)

        A_peplength=[]
        for pep in A["PEP.StrippedSequence"]:
            A_peplength.append(len(pep))
        A["Peptide Length"]=A_peplength

        B_peplength=[]
        for pep in B["PEP.StrippedSequence"]:
            B_peplength.append(len(pep))
        B["Peptide Length"]=B_peplength

        if input.compare_venn_plotproperty()=="proteingroups":
            a=set(A["PG.ProteinGroups"])
            b=set(B["PG.ProteinGroups"])
        if input.compare_venn_plotproperty()=="peptides":
            if input.compare_venn_ptm()==True:
                ptm=input.compare_venn_foundptms()
                A=A[A["EG.ModifiedPeptide"].str.contains(ptm)]
                B=B[B["EG.ModifiedPeptide"].str.contains(ptm)]
            if input.compare_venn_specific_length()==True:
                A=A[A["Peptide Length"]==int(input.compare_venn_peplength_pick())]
                B=B[B["Peptide Length"]==int(input.compare_venn_peplength_pick())]
            else:
                A=A
                B=B
            a=set(A["EG.ModifiedPeptide"])
            b=set(B["EG.ModifiedPeptide"])
            titlemod="Peptides"
        if input.compare_venn_plotproperty()=="precursors":
            if input.compare_venn_ptm()==True:
                ptm=input.compare_venn_foundptms()
                A=A[A["EG.ModifiedPeptide"].str.contains(ptm)]
                B=B[B["EG.ModifiedPeptide"].str.contains(ptm)]
            if input.compare_venn_specific_length()==True:
                A=A[A["Peptide Length"]==int(input.compare_venn_peplength_pick())]
                B=B[B["Peptide Length"]==int(input.compare_venn_peplength_pick())]
            else:
                A=A
                B=B
            a=set(A["pep_charge"])
            b=set(B["pep_charge"])
        if input.compare_venn_plotproperty()=="peptides_stripped":
            if input.compare_venn_ptm()==True:
                ptm=input.compare_venn_foundptms()
                A=A[A["EG.ModifiedPeptide"].str.contains(ptm)]
                B=B[B["EG.ModifiedPeptide"].str.contains(ptm)]
            if input.compare_venn_specific_length()==True:
                A=A[A["Peptide Length"]==int(input.compare_venn_peplength_pick())]
                B=B[B["Peptide Length"]==int(input.compare_venn_peplength_pick())]
            else:
                A=A
                B=B
            a=set(A["PEP.StrippedSequence"])
            b=set(B["PEP.StrippedSequence"])

        df=pd.DataFrame()
        Ab=list(a-b)
        aB=list(b-a)
        AB=list(a&b)
        df=pd.concat([df,pd.Series(Ab,name=input.compare_software1())],axis=1)
        df=pd.concat([df,pd.Series(aB,name=input.compare_software2())],axis=1)
        df=pd.concat([df,pd.Series(AB,name="Both")],axis=1)
        with io.BytesIO() as buf:
            df.to_csv(buf,index=False)
            yield buf.getvalue() 

#endregion

# ============================================================================= Export Tables 
#region 

    #download table of peptide IDs
    @render.download(filename=lambda: f"Peptide List_{input.searchreport()[0]['name']}.csv")
    def peptidelist():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
        peptidetable=searchoutput[["R.Condition","R.Replicate","PG.Genes","PG.ProteinAccessions","PG.ProteinNames","PG.ProteinGroups","EG.ModifiedPeptide","FG.Charge"]].drop_duplicates().reset_index(drop=True)
        with io.BytesIO() as buf:
            peptidetable.to_csv(buf,index=False)
            yield buf.getvalue()

    #condition or run dropdown for stripped peptide list export
    @render.ui
    def peptidelist_dropdown():
        if input.peptidelist_condition_or_run()=="condition":
            searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
            opts=sampleconditions
            return ui.input_selectize("peptidelist_dropdown_pick","Pick run to export peptide list from",choices=opts)
        if input.peptidelist_condition_or_run()=="individual":
            searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
            opts=resultdf["Cond_Rep"].tolist()
            return ui.input_selectize("peptidelist_dropdown_pick","Pick run to export peptide list from",choices=opts)

    #download list of stripped peptide IDs of specific length
    @render.download(filename=lambda: f"Stripped Peptide List_{input.peptidelist_dropdown_pick()}_{input.strippedpeptidelength()}-mers.csv")
    def strippedpeptidelist():
        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()
        if input.peptidelist_condition_or_run()=="condition":
            placeholder=searchoutput[searchoutput["R.Condition"]==input.peptidelist_dropdown_pick()]["PEP.StrippedSequence"].drop_duplicates().reset_index(drop=True)

            df=pd.DataFrame()
            df["PEP.StrippedSequence"]=placeholder
            lengths=[]
            for pep in placeholder:
                lengths.append(len(pep))
            df["Peptide Length"]=lengths
            outputdf=df[df["Peptide Length"]==input.strippedpeptidelength()].drop(columns=["Peptide Length"])
            with io.BytesIO() as buf:
                outputdf.to_csv(buf,header=False,index=False)
                yield buf.getvalue()
        if input.peptidelist_condition_or_run()=="individual":
            placeholder=searchoutput[searchoutput["Cond_Rep"]==input.peptidelist_dropdown_pick()]["PEP.StrippedSequence"].drop_duplicates().reset_index(drop=True)

            df=pd.DataFrame()
            df["PEP.StrippedSequence"]=placeholder
            lengths=[]
            for pep in placeholder:
                lengths.append(len(pep))
            df["Peptide Length"]=lengths
            outputdf=df[df["Peptide Length"]==input.strippedpeptidelength()].drop(columns=["Peptide Length"])
            with io.BytesIO() as buf:
                outputdf.to_csv(buf,header=False,index=False)
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
        cvproteintable=cvproteintable.reset_index()
        with io.BytesIO() as buf:
            cvproteintable.to_csv(buf,index=False)
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
        cvprecursortable=cvprecursortable.reset_index()
        with io.BytesIO() as buf:
            cvprecursortable.to_csv(buf,index=False)
            yield buf.getvalue()
    
    #download table of MOMA precursors for a specified run
    @render.download(filename=lambda: f"MOMA Table_{input.searchreport()[0]['name']}.csv")
    def moma_download():
        #RT tolerance in s
        rttolerance=input.rttolerance()
        #MZ tolerance in m/z
        mztolerance=input.mztolerance()
        #IM tolerance in 1/K0
        imtolerance=input.imtolerance()

        searchoutput,resultdf,sampleconditions,maxreplicatelist,averagedf,numconditions,repspercondition,numsamples=variables_dfs()

        sample=input.cond_rep()

        columns=["EG.ModifiedPeptide","FG.Charge","EG.IonMobility","EG.ApexRT","FG.PrecMz"]
        df=searchoutput[searchoutput["Cond_Rep"]==sample][["EG.ModifiedPeptide","FG.Charge","EG.IonMobility","EG.ApexRT","FG.PrecMz"]].sort_values(["EG.ApexRT"]).reset_index(drop=True)
        coelutingpeptides=pd.DataFrame(columns=columns)
        for i in range(len(df)):
            if i+1 not in range(len(df)):
                break
            #rtpercentdiff=(abs(df["EG.ApexRT"][i]-df["EG.ApexRT"][i+1])/df["EG.ApexRT"][i])*100
            rtdiff=abs(df["EG.ApexRT"][i]-df["EG.ApexRT"][i+1])
            mzdiff=abs(df["FG.PrecMz"][i]-df["FG.PrecMz"][i+1])
            imdiff=abs(df["EG.IonMobility"][i]-df["EG.IonMobility"][i+1])
            if rtdiff <= rttolerance and mzdiff <= mztolerance and imdiff >= imtolerance:
                coelutingpeptides.loc[len(coelutingpeptides)]=df.iloc[i].tolist()
                coelutingpeptides.loc[len(coelutingpeptides)]=df.iloc[i+1].tolist()

        #adding a column for a rough group number for each group of peptides detected
        for i in range(len(coelutingpeptides)):
            if i+1 not in range(len(coelutingpeptides)):
                break
            #rtpercentdiff=(abs(coelutingpeptides["EG.ApexRT"][i]-coelutingpeptides["EG.ApexRT"][i+1])/coelutingpeptides["EG.ApexRT"][i])*100
            rtdiff=abs(coelutingpeptides["EG.ApexRT"][i]-coelutingpeptides["EG.ApexRT"][i+1])
            mzdiff=abs(coelutingpeptides["FG.PrecMz"][i]-coelutingpeptides["FG.PrecMz"][i+1])
            imdiff=abs(coelutingpeptides["EG.IonMobility"][i]-coelutingpeptides["EG.IonMobility"][i+1])
            if rtdiff <= rttolerance and mzdiff <= mztolerance and imdiff >= imtolerance:
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

# ============================================================================= Raw Data
#region
    # ====================================== Multi-File Import
    #choose whether to import data from individual file names or from a directory
    @render.ui
    def rawfile_input_ui():
        if input.file_or_folder()=="individual":
            return ui.input_text_area("rawfile_input","Paste the path for each .d file you want to upload (note: do not leave whitespace at the end):",width="1500px",autoresize=True,placeholder="ex - C:\\Users\\Data\\K562_500ng_1_Slot1-49_1_3838.d")
        if input.file_or_folder()=="directory":
            return ui.input_text_area("rawfile_input","Paste the path for the directory containing the raw files to upload (note: do not leave whitespace at the end):",width="1500px",autoresize=True,placeholder="ex - C:\\Users\\Data")

    #take text input for data paths and make dictionaries of frame data
    @reactive.calc
    def rawfile_list():
        if input.file_or_folder()=="individual":
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
        if input.file_or_folder()=="directory":
            os.chdir(input.rawfile_input())
            cwd=os.getcwd()
            filelist=[]
            for file in os.listdir():
                if ".d" in file:
                    filelist.append(cwd+"\\"+file)
            MSframedict=dict()
            precursordict=dict()
            samplenames=[]
            for run in filelist:
                frames=pd.DataFrame(atb.read_bruker_sql(run)[2])
                MSframedict[run]=frames[frames["MsMsType"]==0].reset_index(drop=True)
                precursordict[run]=pd.DataFrame(atb.read_bruker_sql(run)[3])
                samplenames.append(run.split("\\")[-1])
            return MSframedict,precursordict,samplenames

    #for directory input, show what files were found in the directory
    @render.text
    def uploadedfiles():
        if input.file_or_folder()=="directory":
            try:
                MSframedict,precursordict,samplenames=rawfile_list()
                printsamplenames="\n".join(str(el) for el in samplenames)
            except:
                return ""
            return printsamplenames

    # ====================================== TIC Plot
    #render ui for checkboxes to plot specific runs
    @render.ui
    def rawfile_checkboxes_tic():
        MSframedict,precursordict,samplenames=rawfile_list()
        opts=dict()
        keys=MSframedict.keys()
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
                    ax[i].set_ylabel("Intensity",fontsize=input.axisfont())
                    ax[0].set_title("Total Ion Chromatogram",fontsize=input.titlefont())
                    ax[i].set_axisbelow(True)
                    ax[i].grid(linestyle="--")
                    ax[i].xaxis.set_minor_locator(MultipleLocator(1))
                    legend=ax[i].legend(loc="upper left")
                    for z in legend.legend_handles:
                        z.set_linewidth(5)
                ax[i].set_xlabel("Time (min)",fontsize=input.axisfont())
            else:
                fig,ax=plt.subplots()
                for run in checkgroup:
                    x=MSframedict[run]["Time"]/60
                    y=MSframedict[run]["SummedIntensities"]
                    ax.plot(x,y,label=run.split("\\")[-1],linewidth=0.75)
                ax.set_xlabel("Time (min)",fontsize=input.axisfont())
                ax.set_ylabel("Intensity",fontsize=input.axisfont())
                ax.set_title("Total Ion Chromatogram",fontsize=input.titlefont())
                ax.set_axisbelow(True)
                ax.grid(linestyle="--")
                ax.xaxis.set_minor_locator(MultipleLocator(1))
                #legend=ax.legend(loc='center left', bbox_to_anchor=(1,0.5),prop={'size':10})
                legend=ax.legend(loc="upper left")
                for z in legend.legend_handles:
                    z.set_linewidth(5)
               
    # ====================================== BPC Plot
    #render ui for checkboxes to plot specific runs
    @render.ui
    def rawfile_checkboxes_bpc():
        MSframedict,precursordict,samplenames=rawfile_list()
        opts=dict()
        keys=MSframedict.keys()
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
                    ax[i].set_ylabel("Intensity",fontsize=input.axisfont())
                    ax[0].set_title("Base Peak Chromatogram",fontsize=input.titlefont())
                    ax[i].set_axisbelow(True)
                    ax[i].grid(linestyle="--")
                    ax[i].xaxis.set_minor_locator(MultipleLocator(1))
                    legend=ax[i].legend(loc="upper left")
                    for z in legend.legend_handles:
                        z.set_linewidth(5)
                ax[i].set_xlabel("Time (min)",fontsize=input.axisfont())
            else:
                fig,ax=plt.subplots()
                for run in checkgroup:
                    x=MSframedict[run]["Time"]/60
                    y=MSframedict[run]["MaxIntensity"]
                    ax.plot(x,y,label=run.split("\\")[-1],linewidth=0.75)
                ax.set_xlabel("Time (min)",fontsize=input.axisfont())
                ax.set_ylabel("Intensity",fontsize=input.axisfont())
                ax.set_title("Base Peak Chromatogram",fontsize=input.titlefont())
                ax.set_axisbelow(True)
                ax.grid(linestyle="--")
                ax.xaxis.set_minor_locator(MultipleLocator(1))
                #legend=ax.legend(loc='center left', bbox_to_anchor=(1,0.5),prop={'size':10})
                legend=ax.legend(loc='upper left')
                for z in legend.legend_handles:
                    z.set_linewidth(5)      

    # ====================================== Accumulation Time
    #render ui for checkboxes to plot specific runs
    @render.ui
    def rawfile_checkboxes_accutime():
        MSframedict,precursordict,samplenames=rawfile_list()
        opts=dict()
        keys=MSframedict.keys()
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
                    ax[i].set_ylabel("Accumulation Time (ms)",fontsize=input.axisfont())
                    ax[0].set_title("Accumulation Time Chromatogram",fontsize=input.titlefont())
                    ax[i].set_axisbelow(True)
                    ax[i].grid(linestyle="--")
                    ax[i].xaxis.set_minor_locator(MultipleLocator(1))
                    legend=ax[i].legend(loc="upper left")
                    for z in legend.legend_handles:
                        z.set_linewidth(5)
                ax[i].set_xlabel("Time (min)",fontsize=input.axisfont())
            else:
                fig,ax=plt.subplots()
                for run in checkgroup:
                    x=MSframedict[run]["Time"]/60
                    y=MSframedict[run]["AccumulationTime"]
                    ax.plot(x,y,label=run.split("\\")[-1],linewidth=0.75)
                ax.set_xlabel("Time (min)",fontsize=input.axisfont())
                ax.set_ylabel("Accumulation Time (ms)",fontsize=input.axisfont())
                ax.set_title("Accumulation Time Chromatogram",fontsize=input.titlefont())
                ax.set_axisbelow(True)
                ax.grid(linestyle="--")
                ax.xaxis.set_minor_locator(MultipleLocator(1))
                legend=ax.legend(loc='center left', bbox_to_anchor=(1,0.5),prop={'size':10})
                for z in legend.legend_handles:
                    z.set_linewidth(5)

    # ====================================== EIC Plot
    @render.ui
    def rawfile_buttons_eic():
        MSframedict,precursordict,samplenames=rawfile_list()
        opts=dict()
        keys=MSframedict.keys()
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
    @reactive.event(input.eic_load_rawfile)
    def eic_rawfile_import():
        rawfile=atb.TimsTOF(input.rawfile_pick_eic())
        return rawfile
    #plot EIC for input mass
    @reactive.effect
    def _():
        @render.plot(width=input.eic_width(),height=input.eic_height())
        def eic():
            rawfile=eic_rawfile_import()
            try:
                mz=float(input.eic_mz_input())
                ppm_error=float(input.eic_ppm_input())
                
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

                fig,ax=plt.subplots()
                ax.plot(eic_df["rt_values_min"],eic_df["intensity_values"],linewidth=0.5)
                if input.include_mobility()==True:
                    ax.set_title(input.rawfile_pick_eic().split("\\")[-1]+"\n"+"EIC: "+str(input.eic_mz_input())+", Mobility: "+str(input.mobility_input_value()))
                else:
                    ax.set_title(input.rawfile_pick_eic().split("\\")[-1]+"\n"+"EIC: "+str(input.eic_mz_input()))
                ax.xaxis.set_minor_locator(MultipleLocator(1))
            except:
                fig,ax=plt.subplots()
            ax.set_xlabel("Time (min)",fontsize=input.axisfont())
            ax.set_ylabel("Intensity",fontsize=input.axisfont())
            ax.set_axisbelow(True)
            ax.grid(linestyle="--")

    # ====================================== EIM Plot
    @render.ui
    def rawfile_buttons_eim():
        MSframedict,precursordict,samplenames=rawfile_list()
        opts=dict()
        keys=MSframedict.keys()
        labels=samplenames
        for x,y in zip(keys,labels):
            opts[x]=y
        return ui.input_radio_buttons("rawfile_pick_eim","Pick file to plot data for:",choices=opts,width="800px")
    @reactive.calc
    @reactive.event(input.eim_load_rawfile)
    def eim_rawfile_import():
        rawfile=atb.TimsTOF(input.rawfile_pick_eim())
        return rawfile
    #plot EIM for input mass
    @reactive.effect
    def _():
        @render.plot(width=input.eim_width(),height=input.eim_height())
        def eim():
            rawfile=eim_rawfile_import()
            try:
                mz=float(input.eim_mz_input())
                ppm_error=float(input.eim_ppm_input())
                low_mz=mz/(1+ppm_error/10**6)
                high_mz=mz*(1+ppm_error/10**6)

                eim_df=rawfile[:,:,0,low_mz: high_mz].sort_values("mobility_values")

                fig,ax=plt.subplots()
                ax.plot(eim_df["mobility_values"],eim_df["intensity_values"],linewidth=0.5)
                ax.set_title(input.rawfile_pick_eim().split("\\")[-1]+"\n"+"EIM: "+str(input.eim_mz_input()))
                ax.xaxis.set_minor_locator(MultipleLocator(0.01))
            except:
                fig,ax=plt.subplots()
            ax.set_xlabel("Ion Mobility ($1/K_{0}$)",fontsize=input.axisfont())
            ax.set_ylabel("Intensity",fontsize=input.axisfont())
            ax.set_axisbelow(True)
            ax.grid(linestyle="--")

#endregion

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

app=App(app_ui,server)