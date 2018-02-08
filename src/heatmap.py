import matplotlib.pyplot as plt
import pandas as pd
import matplotlib as mpl
import seaborn as sns
import itertools
# from joblib import delayed, Parallel
#
def ax_plot(data_dfs, ax, key, leak, idx, i, **kwargs):

    delay_years = kwargs.get('delay_years', [0, 10 , 20])
    offset = kwargs['offset']
    bar_width = kwargs.get('bar_width', 0.15)

    for j, year in enumerate(delay_years):
        temp_df = data_dfs[key][year]
        temp_df = temp_df.loc[temp_df['Leak']==leak,:]

        ax.bar(left = 1 + offset * j + idx * bar_width,
               height = i+1,
               width = bar_width,
               bottom = i,
               color=temp_df.loc[i,'Color'],
               linewidth=0)
    pass

class Main_figure:
    def __init__(self):
        self._start_delay_kwargs = {'size': 14,
                                      'horizontalalignment': 'center',
                                      'verticalalignment': 'center'}
        pass

    def figure_data(self, df, scenarios, leak_rates=range(1,6), kind='RF',
                    delay_years=[0,20]):
        self.kind=kind #Use for selecting colorbar units label
        leak_values = ['NGCC ' + str(x) + '%' for x in leak_rates]
        self.years = set(df['Time'])
        self.data_dfs = {}
        self.scenarios=scenarios
        for key in self.scenarios.keys():
            self.data_dfs[key] = {}

            for start in delay_years:
                temp_df_coal = df.loc[(df['CCS']==self.scenarios[key]['Coal CCS']) &
                                 (df['Fuel']=='Coal') &
                                 (df['Start year']==start)]
                temp_df_gas = df.loc[(df['CCS']==self.scenarios[key]['Gas CCS']) &
                                 (df['Fuel']=='NG') &
                                 (df['Methane']==self.scenarios[key]['Methane']) &
                                 (df['Start year']==start)]
                temp_df = pd.concat([temp_df_coal, temp_df_gas])

                # Populate a temporary list of dfs that get concatenated
                temp_list = []
                for leak in leak_values:
                    diff = pd.DataFrame(columns=['Difference', 'Leak', 'Time'])
                    diff.loc[:,'Difference'] = (temp_df.loc[temp_df['Fuel']=='Coal', kind].values -
                        temp_df.loc[(temp_df['Fuel']=='NG')&(temp_df['Leak']==leak), kind].values)
                    diff.loc[:,'Leak'] = leak
                    diff.loc[:,'Time'] = temp_df.loc[temp_df['Fuel']=='Coal', 'Time'].values

                    temp_list.append(diff)

                self.data_dfs[key][start] = pd.concat(temp_list)

#         return data_dfs

    def find_max_abs(self, data, leak_rates=range(1,6), data_column='Difference'):
        """"
        Returns the maximum absolute value from the dataframe.
        Used to scale the colorbar.

        -----
        data: dataframe input
        leak_rates: string or list of values that are expected in the 'leak' column of
                    the dataframe
        data_column: string or list of dataframe column to find the abs max of
        """
        leak_values = ['NGCC ' + str(x) + '%' for x in leak_rates]


        filtered_data = data.loc[data['Leak'].isin(leak_values), data_column].copy()

        max_value = filtered_data.values.max()
        min_value = filtered_data.values.min()
        self.abs_max = max(max_value, abs(min_value))

        return self.abs_max

    def set_cbar_scale(self):
        'Set the cbar scale with one set of data. Can apply to a second set'
        self.df_list = []
        for key1 in self.data_dfs.keys():
            for key2 in self.data_dfs[key1].keys():
                self.df_list.append(self.data_dfs[key1][key2])

        self.cbar_scale = self.find_max_abs(pd.concat(self.df_list))

    def set_color_values(self):
        # self.df_list = []
        # for key1 in self.data_dfs.keys():
        #     for key2 in self.data_dfs[key1].keys():
        #         self.df_list.append(self.data_dfs[key1][key2])

        # cbar_scale = self.find_max_abs(pd.concat(self.df_list))

        _norm = mpl.colors.Normalize(vmin=-self.cbar_scale,
                                     vmax=self.cbar_scale)

        self.c = plt.cm.ScalarMappable(norm=_norm, cmap='RdBu')
        c_lambda = lambda x: self.c.to_rgba(x)
        for key1 in self.data_dfs.keys():
            for key2 in self.data_dfs[key1].keys():
                self.data_dfs[key1][key2].loc[:,'Color'] = self.data_dfs[key1][key2].loc[:,'Difference'].apply(c_lambda)
#         return self.data_dfs, self.c

    def make_ticks(self, idx, leak_rates, offset, bar_width):

        ticks = [1 + idx * offset + i * bar_width for i in range(len(leak_rates))]

        return ticks

    def ax_plot(self, ax, key, leak, idx, i):

        for j, year in enumerate(self.delay_years):
            temp_df = self.data_dfs[key][year]
            temp_df = temp_df.loc[temp_df['Leak']==leak,:]

            ax.bar(left = 1 + self.offset * j + idx * self.bar_width,
                   height = i+1,
                   width = self.bar_width,
                   bottom = i,
                   color=temp_df.loc[i,'Color'],
                   linewidth=0)
        pass

    def plot_heatmap(self, leak_rates=range(1,6), delay_years=[0,20],
                     font_scale=1.0, figsize=[13,6], cbar_pad=0.05,
                     bar_width=0.15, rows=2, cols=4, group_spacing=1.0,
                     scenario_keys=None, cbar=True, **kwargs):
        """

        inputs:
            leak_rates: list
                Values of natural gas leakage rates to include
            delay_years: list
                Values of how long CCS is delayed
            font_scale: float
                scale value for font size
            figsize: list
                width and height of figure in inches. converted to a tuple in
                the function
            cbar_pad: float
                Fraction of original axes between colorbar and new image axes
            bar_width: float or None
                Width of each individual stacked bar. If None, use default of 0.25 inches
            rows: int
                Number of subplot rows for the figure
            cols: int
                Number of subplot columns for the figure
            group_spacing: float
                Spacing between each set of columns in inches
            scenario_keys: dict
                scenarios to include in the figure - could be a subset of
                scenarios in the original dataframe
            cbar: bool
                If True, add a colorbar to the figure.

        """
        label_dict = kwargs.get('label_dict',
                                dict(
                                x=0.0,
                                y=1.02,
                                ha='center',
                                size=8,
                                weight='bold'
                                ))
        title_dict = kwargs.get('title_dict',
                                dict(
                                size=8
                                ))
        ylabel_dict = kwargs.get('ylabel_dict',
                                 dict(
                                 size=8
                                 ))
        year_label_dict = kwargs.get('year_label_dict',
                                     dict(
                                     size=8,
                                     y=-0.15,
                                     horizontalalignment='center'
                                     ))
        year_label_loc = kwargs.get('year_label_loc',
                [(x + 1) / (len(delay_years) + 1)
                 for x in range(len(delay_years))]
            )
        ytick_label_dict = kwargs.get('ytick_label_dict',
                                     dict(
                                     # size=7,
                                     labelsize=7,
                                     length=4,
                                     width=1
                                     ))
        xtick_label_dict = kwargs.get('xtick_label_dict',
                                     dict(
                                     # size=7,
                                     labelsize=7,
                                     length=4,
                                     width=1
                                     ))
        cbar_arrow_dict = kwargs.get('cbar_arrow_dict',
                                     dict(
                                     fontsize=7
                                     ))
        arrowprops = kwargs.get('arrowprops',
                                dict(
                                facecolor='black',
                                width = .75,
                                # headwidth=3
                                ))
        # Provide a dictionary with the key for a facet and a title
        alt_titles = kwargs.get('alt_titles', None)

        cbar_arrow_x = kwargs.get('cbar_arrow_x', 1.43 - (cbar_pad - 0.05))





        # Adjust figure size if not adding colorbar
        if not cbar:
            # Default cbar size is 15% of original axes
            shrink = 0.15 + cbar_pad
            figsize[0] *= (1 - shrink)

        self.bar_width = bar_width
        self.delay_years = delay_years

        # identify scenarios in top row, bottom row, and first column
        keys_list = list(scenario_keys.keys())
        num_scenarios = len(scenario_keys)
        half_scenarios = int(num_scenarios / 2)
        top_row_keys = keys_list[:half_scenarios]
        bottom_row_keys = keys_list[half_scenarios:]
        first_column_top = keys_list[0]
        first_column_bottom = keys_list[half_scenarios]

        sns.set_style('white')

        _figsize = tuple(figsize)
        fig, axs = plt.subplots(rows, cols, figsize=_figsize, sharey=True,
                                sharex=True)

        # Distance from start of one bar group to the start of the next
        offset = bar_width * len(leak_rates) + group_spacing
        self.offset = offset

        self.xticks = []
        for idx in range(len(delay_years)):
            _xticks = self.make_ticks(idx, leak_rates, offset, bar_width)
            self.xticks.extend(_xticks)

        # list of tick labels - only set up for 1-5% leakage
        leak_values = ['NGCC {}%'.format(x) for x in leak_rates]
        percents = [x[-2:] if int(x[-2]) % 2 == 1 else '' for x in leak_values]
        # empty = [''] * len(leak_values)

        # Last item in the list is empty
        # Create a list like ['1%', '', '3%', '', ...]
        self.xticklabels = percents * len(delay_years)

        # self.xticklabels = ['1%', '', '3%', '', '5%'] * len(delay_years)

        if not scenario_keys:
            scenario_keys = self.scenarios.keys()
#         scenario_keys.sort()

        # kwargs for external plotting function
        # kwargs = {
        #     # data_dfs = self.data_dfs,
        #     'offset': self.offset,
        #     'delay_years': self.delay_years,
        #     'bar_width': self.bar_width
        # }

        # create each subplot
        for key, ax in zip(scenario_keys, axs.flat):
            # ax.set_aspect(aspect='equal', adjustable='box-forced')

            # Plot bar for each of the leak rates
            # One bar for each of the delay year values
            for idx, leak in enumerate(leak_values):

                # Create 1 year of the bar at a time
                for i in self.years: #range(100):
                    self.ax_plot(ax, key, leak, idx, i)
                    # for j in range(len(delay_years)):
                # if n_jobs !=1:
                #     # Parallel(n_jobs=2)(delayed(sqrt)(i ** 2) for i in range(10))
                #     Parallel(n_jobs=n_jobs)(delayed(ax_plot)
                #         (self.data_dfs, ax, key, leak, idx, i, **kwargs) for i in range(100))
                # else:
                    # for i in range(100):
                        # self.ax_plot(ax, key, leak, idx, i)
                    # self.ax_plot(ax, key, leak, idx, i)

                # Only add the title for upper subplots
                if key in top_row_keys:
                    if alt_titles:
                        title = alt_titles.get(key, None)
                    else:
                        title = '{} SCPC,\n{} NGCC'.format(
                            self.scenarios[key]['Coal CCS'],
                            self.scenarios[key]['Gas CCS']
                        )
                        #
                        # self.scenarios[key]['Coal CCS']  + ' SCPC, \n' + \
                        #         self.scenarios[key]['Gas CCS']  + ' NGCC CCS'

                    ax.set_title(title, **title_dict)


                # # Add years of delay to bottom subplots
                # if key in bottom_row_keys:
                #     for idx, year in enumerate(delay_years):
                #         # Not sure why, but 0.5 gives a good placement
                #         loc = (0.5 + idx) / len(delay_years)
                #         txt = 'Year {}'.format(year)
                #
                #         # use ax.transAxes to transform axis coordinates
                #         ax.text(loc, -0.15, txt, transform=ax.transAxes,
                #                 **self._start_delay_kwargs)

                #subplot labeling
                # ax.text(0.47, 0.5, key, transform=ax.transAxes, size=14)

                ax.set_xticks([a for a in self.xticks])
                ax.set_xticklabels(self.xticklabels)
                ax.tick_params(axis='x', which='both',
                               **xtick_label_dict)
                ax.tick_params(axis='y', which='both',
                               **ytick_label_dict)


        # Set y-axis labels on the first and mid axes
        # flatten() converts a 2d array to a 1-d, row-order by default
        # half_index = int(len(scenario_keys) / 2)
        axs = axs.flatten()
        axs[0].set_ylabel('Years after start\n(Constant leakage)',
                          **ylabel_dict)
        axs[half_scenarios].set_ylabel('Years after start\n(Reduce leakage)',
                                       **ylabel_dict)

        # Try this outside the loop above to avoid bold font
        for ax, key in zip(axs, scenario_keys):
            # x_label = 1 / len(delay_years)
            x_label = 0.0
            # ax.text(0.47, 0.5, key, transform=ax.transAxes, size=8)
            ax.text(s=key, transform=ax.transAxes, **label_dict)

        # Add years of delay to bottom subplots
        # Doing this in the loop of ax objects above led to bold font
        for ax in axs[half_scenarios:]:
            for year, loc in zip(delay_years, year_label_loc):
                # loc = (idx + 1) / (len(delay_years) + 1)
                txt = 'Year {}'.format(year)

                # use ax.transAxes to transform axis coordinates
                ax.text(x=loc, s=txt, transform=ax.transAxes,
                        **year_label_dict)

        # Set y-lim
        plt.ylim(0,100)
        plt.tight_layout()

        if cbar:
            # Text objects are being plotted on the last axis (bottom right)
            # so they need to be well outside the actual plot. The coordinates
            # are using a transformed axis.

            # With a pad of 0.05 the x placement was 1.43
            # self.cbar_arrow_x = 1.43 - (cbar_pad - 0.05)
            self.cbar_arrow_x = cbar_arrow_x

            # arrow_props = dict(
            #     facecolor='black',
            #     width = 1,
            #     headwidth=6
            # )

            plt.annotate('SCPC Higher', xy=(cbar_arrow_x, 2.1),
                         xycoords=ax.transAxes,
                         xytext=(cbar_arrow_x, 1.75), textcoords=ax.transAxes,
                         ha='center', arrowprops=arrowprops, rotation=270,
                         **cbar_arrow_dict)

            plt.annotate('SCPC Lower', xy=(cbar_arrow_x, 0.1),
                         xycoords=ax.transAxes,
                         xytext=(cbar_arrow_x, 0.7), textcoords=ax.transAxes,
                         ha='center', arrowprops=arrowprops, rotation=270,
                         **cbar_arrow_dict)



            self.c._A = [] # I have no clue why I need to do this
            cbar = fig.colorbar(self.c, ax=axs.ravel().tolist(), pad=cbar_pad)
            if self.kind == 'RF':
                cbar.ax.set_title('$W \ m^{-2}$', size = 8)
            elif self.kind == 'CRF':
                cbar.ax.set_title('$W \ m^{-2} \ y$', size = 8)


            # Auto set the colorbar tick labels/positions
            cticks = [self.abs_max * x for x in [0.9, 0.45, 0, -0.45, -0.9]]

            # Make the labels absolute value, but still with scientific notation
            cticklables = ['{0:.1e}'.format(abs(i)) for i in cticks]

            cbar.set_ticks(cticks)
            cbar.set_ticklabels(cticklables)
            cbar.ax.yaxis.set_ticks_position('right')
            cbar.ax.tick_params(**ytick_label_dict)

        sns.despine()
