import pandas as pd
import numpy as np


size = 1000 # MW
hours = 365 * 24
capacity_factor = 0.8

generation = size * hours * capacity_factor #MWh/yr

# Hardcoded/calculated emission values for natural gas and NGCC plants
Mbtu_to_MJ = 1.05506 # MJ per Mbtu, used for heat rate conversion
ngcc_ng = 133.4 #kg NG for 1MWh NGCC w/o CCS from PPFM (uses NG energy content of 52.43 MJ/kg)
ngcc_ccs_ng = 150.2 #kg NG for 1MWh NGCC w CCS from PPFM (uses NG energy content of 52.43 MJ/kg)
ngcc_MJ = 6629 * Mbtu_to_MJ # Convert btu/kWh heat rate to MJ/MWh
ngcc_ccs_MJ = 7466 * Mbtu_to_MJ # Convert btu/kWh heat rate to MJ/MWh
CH4_per_kg_leak = 0.01 #kg methane per % emission per kg NG
CO2_per_MJ = 3.8 / 1000 #kg CO2 per % emission per MJ NG

CH4_per_leak =  ngcc_ng * CH4_per_kg_leak
CH4_per_leak_CCS = ngcc_ccs_ng * CH4_per_kg_leak
base_CO2 = 357 + CO2_per_MJ * ngcc_MJ # From Exhibit 4-8 of Ref. 3
base_CO2_CCS = 40 + CO2_per_MJ * ngcc_ccs_MJ # From Exhibit 4-22 of Ref. 3

# Dictionary of emission values for NGCC power plants
# Leak emissions are per percent leakage rate
ng_emissions = {'0%': {'Fixed': {'CO2': base_CO2,
                                   'CH4': 0},
                           'Leak': {'CO2': 0,
                                   'CH4': CH4_per_leak}
                         },
                 '90%': {'Fixed': {'CO2': base_CO2_CCS,
                                   'CH4': 0},
                           'Leak': {'CO2': 0,
                                   'CH4': CH4_per_leak_CCS}
                         }
               }


# Hardcoded/calculated emission values for coal and SCPC plants
coal_co2 = 3.75E-2 #kg co2 per kg I6 coal from NETL 2014 NG report
coal_ch4 = 7.64E-03 #kg ch4 per kg I6 coal from NETL 2014 NG report
scpc_coal = 325.8 #kg coal for 1MWh SCPC w/o CCS from PPFM with heat rate of 8379 btu/kWh
scpc_direct_co2 = 773.7 #kg co2 from 1MWh SCPC w/o CCS from PPFM with heat rate of 8379 btu/kWh
scpc_co2 = scpc_direct_co2 + (scpc_coal * coal_co2)
scpc_ch4 = scpc_coal * coal_ch4


scpc_ccs_coal = 408.6 #kg coal for 1MWh SCPC w/ CCS from PPFM with heat rate of 10508 btu/kWh
scpc_ccs_co2 = 97 #kg co2 from 1MWh SCPC w/ CCS from PPFM with heat rate of 10508 btu/kWh
scpc_ccs_co2_product = 873.1 #kg co2 product from 1MWh SCPC w/ CCS from PPFM
scpc_ccs_co2 = scpc_ccs_co2 + (scpc_ccs_coal * coal_co2)
scpc_ccs_ch4 = scpc_ccs_coal * coal_ch4

# All 111b values are based on emissions of 1,400 lb/MWh gross from final EPA 111(b) rule
scpc_111b_coal = 342.1 #kg coal for 1MWh SCPC w/ CCS from PPFM
scpc_111b_co2 = 682.2 #kg co2 from 1MWh SCPC w/ CCS from PPFM
scpc_111b_co2_product = 122 #kg co2 product from 1MWh SCPC w/ CCS from PPFM
scpc_111b_co2 = scpc_111b_co2 + (scpc_111b_coal * coal_co2)
scpc_111b_ch4 = scpc_111b_coal * coal_ch4

# Dictionary of emission values for NGCC power plants
coal_emissions = {'90%': {'CO2':scpc_ccs_co2,
                          'CH4': scpc_ccs_ch4},
                  '0%': {'CO2':scpc_co2,
                          'CH4':scpc_ch4},
                  '16%':{'CO2':scpc_111b_co2,
                          'CH4': scpc_111b_ch4}
                 }

def emissions(coal_emissions=coal_emissions, ng_emissions=ng_emissions,
              CCS_start=0, leakage_drop_by=10,
              leak_values=range(1,6), year_to_90CCS=20, life=40):
    """
    Create CO2 and CH4 emission functions for each power plant scenario. All
    natural gas scenarios include both constant leakage rates and leakage rates
    that are reduced by half over time.

    inputs:
        coal_emissions: dict
            Dictionary of CO2 and CH4 emission values for each CCS capture rate
        ng_emissions: dict
            Dictionary of CO2 and CH4 emission values for each CCS capture rate
            with additional keys for fixed values and values that vary by leakage
        CCS_start: int
            Year of operation that CCS begins
        leakage_drop_by: int
            Year of operation where methane emissions have dropped
            by half of initial value.
        leak_values: list or other iterable
            Numeric values representing leakage rate scenarios. 1 = 1%, etc.
        year_to_90CCS: int
            If coal CCS starts at 111b levels (16%), this is the year where it
            changes to 90% capture.
        life: int
            Lifetime of the power plants
    outputs:
        emissions_df: dataframe
            A single tidy dataframe with all emission scenarios
        df_list: list of dataframes
            A list with individual dataframes for each specific emission scenario
    """
    end = 100
    tstep = 0.01
    time = np.linspace(0, end, num=int(end/tstep+1)) #time array


    leak = {} # dictionary of leak values
    for value in leak_values:
        # Change values to integer if possible
        if (type(value) == float) and (value - int(value) == 0):
            value = int(value)

        key = 'NGCC ' + str(value) + '%' # define the key for a leak value
        leak[key] = float(value) # Add key and value to the dictionary




    # Empty dataframes for leakage rates (constant and reduced)
    leakage = pd.DataFrame(index=time, columns=leak.keys())
    leakage_drop = pd.DataFrame(index=time, columns=leak.keys())

    for rate in leak.keys():
        #Initial methane emission (or leak) rate
        leakage.loc[:,rate] = leak[rate]

        #Methane emission rate that drops over time. Starts at initial, with a linear
        #decrease until half of initial.
        leakage_drop.loc[:,rate] = leak[rate]
        if rate != 'NGCC 1%':
            # Use linspace to interpolate between values
            leakage_drop.loc[:leakage_drop_by,rate] = np.linspace(leak[rate],
                                                                 leak[rate]/2,
                                                                 leakage_drop_by/tstep+1)
            leakage_drop.loc[leakage_drop_by:life,rate] = leak[rate]/2
            leakage_drop.loc[life:,rate] = 0

    df_list = []

    # NGCC emissions - don't worry about delayed CCS yet
    for l in leak.keys():
        for ccs in ng_emissions.keys():
            # Constant methane
            df = pd.DataFrame(index=time,
                              columns=['CO2', 'CH4', 'Leak', 'CCS', 'Fuel', 'Methane', 'Start year'])
            df.loc[:,'Start year'] = CCS_start
            df.loc[:,'Methane'] = 'Constant'
            df.loc[:,'Fuel'] = 'NG'
            df.loc[:,'CCS'] = ccs
            df.loc[:,'Leak'] = l
            df.loc[:,'CO2'] = ng_emissions[ccs]['Fixed']['CO2']
            df.loc[:,'CH4'] = (ng_emissions[ccs]['Leak']['CH4']
                               * leakage.loc[:,l].copy())

            # This gets complicated when accounting for delayed CCS start
            if CCS_start > 0:
                df.loc[:CCS_start,'CO2'] = ng_emissions['0%']['Fixed']['CO2'] #*
                                            #np.ones_like(leakage.loc[:CCS_start,l]))
                df.loc[:CCS_start,'CH4'] = ng_emissions['0%']['Leak']['CH4'] * leakage.loc[:CCS_start,l].copy()
            df.loc[life:,['CO2', 'CH4']] = 0
            df_list.append(df)

            # Reduced methane
            df = pd.DataFrame(index=time,
                              columns=['CO2', 'CH4', 'Leak', 'CCS', 'Fuel', 'Methane', 'Start year'])
            df.loc[:,'Start year'] = CCS_start
            df.loc[:,'Methane'] = 'Reduce'
            df.loc[:,'Fuel'] = 'NG'
            df.loc[:,'CCS'] = ccs
            df.loc[:,'Leak'] = l
            df.loc[:,'CO2'] = ng_emissions[ccs]['Fixed']['CO2']
            df.loc[:,'CH4'] = ng_emissions[ccs]['Leak']['CH4'] * leakage_drop.loc[:,l].copy()

            # This gets complicated when accounting for delayed CCS start
            if CCS_start > 0:
                df.loc[:CCS_start,'CO2'] = ng_emissions['0%']['Fixed']['CO2'] #*
                                            #np.ones_like(leakage_drop.loc[:CCS_start,l]))
                df.loc[:CCS_start,'CH4'] = ng_emissions['0%']['Leak']['CH4'] * leakage_drop.loc[:CCS_start,l].copy()
            df.loc[life:,['CO2', 'CH4']] = 0
            df_list.append(df)


    # SCPC emissions
    for ccs in coal_emissions.keys():
        df = pd.DataFrame(index=time,
                              columns=['CO2', 'CH4', 'Leak', 'CCS', 'Fuel', 'Methane', 'Start year'])
        df.loc[:,'Start year'] = CCS_start
        df.loc[:,'Methane'] = '-'
        df.loc[:,'Fuel'] = 'Coal'
        df.loc[:,'CCS'] = ccs
        df.loc[:,'Leak'] = 'SCPC'
        df.loc[:,'CO2'] = coal_emissions[ccs]['CO2']
        df.loc[:,'CH4'] = coal_emissions[ccs]['CH4']
        df.loc[life:,['CO2', 'CH4']] = 0

        if CCS_start > 0:
            df.loc[:CCS_start,'CO2'] = coal_emissions['0%']['CO2']
            df.loc[:CCS_start,'CH4'] = coal_emissions['0%']['CH4']
        df_list.append(df)

    # Concat all dataframes
    emissions_df = pd.concat(df_list)

    # Add one more scenario for CCS that goes from 16% to 90%
    # if year_to_90CCS > 0:# and CCS_start == 0:
    df = emissions_df.loc[(emissions_df['Fuel'] == 'Coal') &
                          (emissions_df['CCS'] == '16%'),:].copy()
    df_90 = emissions_df.loc[(emissions_df['Fuel'] == 'Coal') &
                             (emissions_df['CCS'] == '90%'),:].copy()

    df.loc[year_to_90CCS:, ['CO2', 'CH4']] = (df_90.loc[year_to_90CCS:,
                                                       ['CO2', 'CH4']])

    df.loc[:year_to_90CCS, 'CO2'] = coal_emissions['16%']['CO2']
    df.loc[:year_to_90CCS, 'CH4'] = coal_emissions['16%']['CH4']

    df.loc[:,'CCS'] = '16%-90%'

    # Concat the extra dataframe
    emissions_df = pd.concat([emissions_df, df])
        # df_list.append(df)

    # Set values in the Time column and reset index in both the large dataframe
    # and each of the individual dataframes
    emissions_df.loc[:,'Time'] = emissions_df.index
    emissions_df.reset_index(drop=True, inplace=True)

    # Force numeric data types for emissions and start year
    for col in ['CO2', 'CH4', 'Start year']:
        emissions_df[col] = pd.to_numeric(emissions_df[col])

    # for df in df_list:
    #     df.loc[:,'Time'] = df.index
    #     df.reset_index(drop=True, inplace=True)

    return emissions_df#, df_list
