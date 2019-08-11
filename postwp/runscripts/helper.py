# dictionary mapping the overall categories of the new fbs outputs and the db filenames to look for for each group.
folder_map = {
'filter_changer':
    [
        'fc1exp_pairsmix_ilim15_10yrs.db',
        'fc1exp_pairsmix_ilim60_10yrs.db',
        'fc1exp_pairsmix_ilim30_10yrs.db'
    ],
'footprints':
    [
        'baseline10yrs.db',
        'newA10yrs.db',
        'big_sky_nouiy10yrs.db',
        'big_sky10yrs.db',
        'stuck_rolling10yrs.db',
        'newB10yrs.db',
        'bluer_footprint10yrs.db',
        'gp_heavy10yrs.db'
    ],
'alt_sched':
    [
        'very_alt10yrs.db',
        'very_alt2_rm5illum20_10yrs.db',
        'very_alt_rm510yrs.db',
        'very_alt3_rm5illum40_10yrs.db',
        'very_alt3_rm5illum25_10yrs.db',
        'dec_1exp_pairsmix_10yrs.db',
        'very_alt2_rm5illum40_10yrs.db',
        'very_alt3_rm5illum20_10yrs.db',
        'very_alt2_rm5illum15_10yrs.db',
        'very_alt2_rm5illum50_10yrs.db',
        'very_alt2_rm5illum25_10yrs.db',
        'very_alt3_rm5illum50_10yrs.db',
        'very_alt3_rm5illum15_10yrs.db',
        'very_alt2_rm5illum30_10yrs.db',
        'very_alt3_rm5illum30_10yrs.db'
    ],
'exp_time':
     [
         'exptime_1exp_pairsmix_10yrs.db'
     ],
'baselines':
     [
        'baseline_1exp_nopairs_10yrs.db',
        'baseline_1exp_pairsmix_10yrs.db',
        'baseline_2exp_pairsmix_10yrs.db',
        'baseline_2exp_pairsame_10yrs.db',
        'baseline_1exp_pairsame_10yrs.db',
        'noddf_1exp_pairsame_10yrs.db'
     ],
'rolling_cadence':
    [
        'roll_mod6_sdf0.20mixed_10yrs.db',
        'roll_mod6_sdf0.05mixed_10yrs.db',
        'simple_roll_mod10_sdf0.20mixed_10yrs.db',
        'roll_mod3_sdf0.20mixed_10yrs.db',
        'roll_mod2_sdf0.20mixed_10yrs.db',
        'roll_mod6_sdf0.10mixed_10yrs.db',
        'roll_mod3_sdf0.05mixed_10yrs.db',
        'simple_roll_mod2_sdf0.20mixed_10yrs.db',
        'roll_mod2_sdf0.05mixed_10yrs.db',
        'roll_mod2_sdf0.10mixed_10yrs.db',
        'simple_roll_mod5_sdf0.20mixed_10yrs.db',
        'roll_mod3_sdf0.10mixed_10yrs.db',
        'simple_roll_mod3_sdf0.20mixed_10yrs.db'
    ],
'ToO':
     [
        'too_pairsmix_rate100_10yrs.db',
        'too_pairsmix_rate50_10yrs.db',
        'too_pairsmix_rate1_10yrs.db',
        'too_pairsmix_rate10_10yrs.db'
     ],
'weather':
     [
        'weather_0.60c_10yrs.db',
        'weather_0.40c_10yrs.db',
        'weather_0.20c_10yrs.db',
        'weather_0.10c_10yrs.db',
        'weather_0.90c_10yrs.db',
        'weather_0.30c_10yrs.db',
        'weather_1.10c_10yrs.db',
        'weather_0.70c_10yrs.db',
        'weather_0.80c_10yrs.db'
     ],
'short_expt':
    [
        'shortt_5ns_5ext_pairsmix_10yrs.db',
        'shortt_5ns_1ext_pairsmix_10yrs.db',
        'shortt_2ns_1ext_pairsmix_10yrs.db',
        'shortt_2ns_5ext_pairsmix_10yrs.db'
    ],
'template_gen':
    [
        'templates_w_2.0_1exp_pairsmix_10yrs.db',
        'templates_w_3.0_1exp_pairsmix_10yrs.db',
        'templates_w_4.0_1exp_pairsmix_10yrs.db',
        'templates_w_1.0_1exp_pairsmix_10yrs.db',
        'templates_w_5.0_1exp_pairsmix_10yrs.db'
    ],
'rotator':
    [
        'rotator_1exp_pairsmix_10yrs.db'
    ],
'presto':
    [
        'presto_third_10yrs.db',
        'presto_10yrs.db'
    ],
'stability_test':
    [
        'stability_1offset_43seed10yrs.db',
        'stability_365offset_42seed10yrs.db',
        'stability_30offset_42seed10yrs.db',
        'stability_10offset_42seed10yrs.db',
        'stability_180offset_42seed10yrs.db',
        'stability_-10offset_42seed10yrs.db',
        'stability_1offset_44seed10yrs.db',
        'stability_1offset_42seed10yrs.db'
    ],
'DDF':
    [
        'ddf_0.23deg_1exp_pairsmix_10yrs.db',
        'ddf_pn_0.23deg_1exp_pairsmix_10yrs.db',
        'desc_ddf_pn_0.70deg_1exp_pairsmix_10yrs.db',
        'ddf_0.70deg_1exp_pairsmix_10yrs.db',
        'ddf_pn_0.70deg_1exp_pairsmix_10yrs.db'
    ]
}
for group in folder_map:
    for i, key in enumerate( folder_map[group] ):
        folder_map[group][i] = key.split('.db')[0]
#folder_map