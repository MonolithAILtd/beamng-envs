from typing import Any, Dict


class ScintillaRally:
    @property
    def config(self) -> Dict[str, Any]:
        return {"parts": self.parts,
                "vars": self.vars,
                "paints": self.paints}

    config_filename = "vehicles/scintilla/rally.pc"
    parts = {
        "digidash_cells_top_center": "digidash_cells_top_center_gear",
        "scintilla_pedal_pads": "scintilla_pedal_pads_b",
        "digidash_cells_top_right_widget": "digidash_cells_top_right_text",
        "scintilla_pedal_pad_clutch": "scintilla_pedal_pad_clutch_b",
        "digidash_cells_bottom_left": "digidash_cells_bottom_left_envTemp",
        "scintilla_quarterglass_RL": "scintilla_quarterglass_RL_lightweight",
        "digidash_cells_bottom_center": "digidash_cells_bottom_center_wheelspeed",
        "scintilla_quarterglass_RR": "scintilla_quarterglass_RR_lightweight",
        "digidash_cells_bottom_right_widget": "digidash_cells_bottom_right_input",
        "scintilla_quarterpanel_R": "scintilla_quarterpanel_R",
        "scintilla_radiator": "scintilla_radiator_race",
        "scintilla_rearbody": "scintilla_rearbody_hardtop",
        "scintilla_rearglass_hardtop": "scintilla_rearglass_hardtop_lightweight",
        "scintilla_reverselight_L": "scintilla_reverselight_L",
        "scintilla_reverselight_R": "scintilla_reverselight_R",
        "scintilla_rollcage_hardtop": "scintilla_rollcage_hardtop",
        "scintilla_roof_accessory": "",
        "scintilla_seat_FL": "scintilla_race_seat_FL",
        "scintilla_seat_FR": "scintilla_race_seat_FR",
        "scintilla_shifter_race": "scintilla_shifter_race_sq",
        "scintilla_shiftknob_sq": "scintilla_shiftknob_sq",
        "scintilla_shiftlight": "",
        "scintilla_sideskirt_L": "scintilla_sideskirt_L",
        "scintilla_sideskirt_R": "scintilla_sideskirt_R",
        "scintilla_splitter_F": "",
        "scintilla_spoiler_perf": "scintilla_bigwing_03a",
        "scintilla_steer": "scintilla_steer_02b",
        "scintilla_steering": "scintilla_steering",
        "scintilla_subframe_R": "scintilla_subframe_R",
        "scintilla_sunvisor_hardtop": "",
        "scintilla_suspension_F": "scintilla_suspension_F",
        "scintilla_suspension_R": "scintilla_suspension_R",
        "scintilla_swaybar_F": "scintilla_swaybar_F_race",
        "scintilla_swaybar_R": "scintilla_swaybar_R_race",
        "scintilla_tailgate_hardtop": "scintilla_tailgate_hardtop",
        "scintilla_taillight_L": "scintilla_taillight_L",
        "scintilla_taillight_M": "scintilla_taillight_M",
        "scintilla_taillight_R": "scintilla_taillight_R",
        "scintilla_transaxle": "scintilla_transaxle_6M_SQ",
        "scintilla_transfer_case": "scintilla_transfer_case_clutchex_race",
        "scintilla_undertray_FL": "scintilla_undertray_FL",
        "scintilla_undertray_FR": "scintilla_undertray_FR",
        "scintilla_undertray_M": "scintilla_undertray_M",
        "scintilla_valance_R": "scintilla_valance_R",
        "scintilla_wheeldata_F": "scintilla_wheeldata_F",
        "scintilla_wheeldata_R": "scintilla_wheeldata_R",
        "scintilla_windshield": "scintilla_windshield_lightweight",
        "scintilla_front_output_ratio_race": "scintilla_front_output_ratio_race",
        "digidash_cells_top_left0": "",
        "digidash_cells_top_left1": "",
        "digidash_cells_top_left2": "",
        "paint_design": "scintilla_skin_amateur",
        "digidash_cells_top_right0": "digidash_cells_top_right0_fuelVolume",
        "digidash_cells_top_right1": "digidash_cells_top_right1_waterTemp",
        "digidash_cells_top_right2": "digidash_cells_top_right2_oilTemp",
        "scintilla_DSE": "scintilla_DSE",
        "scintilla_DSE_ABS": "scintilla_DSE_ABS",
        "scintilla_DSE_ESC": "scintilla_DSE_ESC",
        "brakepad_F": "brakepad_F_race",
        "scintilla_DSE_drivemodes": "scintilla_DSE_drivemodes_ICE_race",
        "scintilla_DSE_drivemodes_race": "scintilla_DSE_drivemodes_race",
        "scintilla_DSE_drivemodes_race_default": "scintilla_DSE_drivemodes_race_default_off",
        "scintilla_weightreduction_hardtop": "",
        "scintilla_skidplate": "scintilla_skidplate",
        "n2o_system": "",
        "scintilla_body": "scintilla_body",
        "scintilla_brake_F": "scintilla_brake_F_carbon",
        "scintilla_brake_R": "scintilla_brake_R_carbon",
        "scintilla_bumper_F": "scintilla_bumper_F",
        "scintilla_bumper_R": "scintilla_bumper_R",
        "scintilla_bumpersupport_F": "scintilla_bumpersupport_F",
        "scintilla_bumpersupport_R": "scintilla_bumpersupport_R",
        "scintilla_chassis": "scintilla_chassis",
        "scintilla_coilover_F": "scintilla_coilover_F_rally",
        "scintilla_coilover_R": "scintilla_coilover_R_rally",
        "scintilla_dash": "scintilla_dash_race",
        "soundscape_horn": "soundscape_horn_4",
        "brakepad_R": "brakepad_R_race",
        "skin_race_seat_FL": "skin_race_seat_FL_red",
        "scintilla_differential_R": "scintilla_differential_R_race",
        "scintilla_mirror_L": "scintilla_mirror_L",
        "scintilla_door_L_hardtop": "scintilla_door_L_hardtop",
        "scintilla_door_R_hardtop": "scintilla_door_R_hardtop",
        "scintilla_doorglass_L_hardtop": "scintilla_doorglass_L_hardtop_lightweight",
        "skin_interior": "scintilla_skin_interior_race",
        "scintilla_doorglass_R_hardtop": "scintilla_doorglass_R_hardtop_lightweight",
        "scintilla_quarterpanel_L": "scintilla_quarterpanel_L",
        "scintilla_doorpanel_L": "scintilla_doorpanel_L_lightweight",
        "scintilla_licenseplate_F": "scintilla_licenseplate_F",
        "scintilla_doorpanel_R": "scintilla_doorpanel_R_lightweight",
        "scintilla_lettering_fender_R": "scintilla_lettering_fender_R",
        "scintilla_driveshaft_F": "scintilla_driveshaft_F",
        "scintilla_engine": "scintilla_engine_5.0_v10",
        "skin_race_seat_FR": "skin_race_seat_FR_red",
        "scintilla_engine_5.0_ecu": "scintilla_engine_5.0_ecu_race",
        "wheel_F_5": "wheel_dreid_c70_18x9_F",
        "scintilla_engine_5.0_internals": "scintilla_engine_internals_5.0_race",
        "scintilla_lettering_bumper_F": "scintilla_lettering_bumper_F",
        "scintilla_enginemounts": "scintilla_enginemounts",
        "scintilla_exhaust": "scintilla_exhaust_race",
        "scintilla_frunk": "scintilla_frunk",
        "scintilla_fascia_R": "scintilla_fascia_R_perf",
        "scintilla_oilpan": "scintilla_oilpan_race",
        "scintilla_fender_L": "scintilla_fender_L",
        "scintilla_fender_R": "scintilla_fender_R",
        "scintilla_fender_cover_L": "scintilla_fender_cover_L_perf",
        "scintilla_pedals": "scintilla_pedals_race",
        "scintilla_fender_cover_R": "scintilla_fender_cover_R_perf",
        "scintilla_DSE_TC": "scintilla_DSE_TC_RWD",
        "scintilla_fenderflare_FL": "",
        "scintilla_fenderflare_FL_door": "",
        "scintilla_fenderflare_FR": "",
        "scintilla_fenderflare_FR_door": "",
        "scintilla_fenderflare_RL": "",
        "scintilla_fenderflare_RR": "",
        "scintilla_finaldrive_F": "scintilla_finaldrive_F_race",
        "race_seat_FR": "race_seat_FR",
        "scintilla_finaldrive_R": "scintilla_finaldrive_R_race",
        "tire_F_18x9": "tire_F_245_40_18_tarmac",
        "scintilla_flashers": "", "race_seat_FL": "race_seat_FL",
        "scintilla_fueltank_L": "scintilla_fueltank_L",
        "scintilla_fueltank_R": "scintilla_fueltank_R",
        "scintilla_gauges": "scintilla_gauges",
        "scintilla_halfshafts_F": "scintilla_halfshafts_F",
        "scintilla_halfshafts_R": "scintilla_halfshafts_R",
        "scintilla_headlight_L": "scintilla_headlight_L",
        "scintilla_headlight_R": "scintilla_headlight_R",
        "tire_R_19x11": "tire_R_295_35_19_tarmac",
        "scintilla_hub_F": "scintilla_hub_F_5",
        "scintilla_hood": "scintilla_hood",
        "scintilla_hub_R": "scintilla_hub_R_5",
        "scintilla_differential_F": "scintilla_differential_F_race",
        "scintilla_innerfender_FL": "scintilla_innerfender_FL",
        "scintilla_innerfender_FR": "scintilla_innerfender_FR",
        "scintilla_innerfender_RL": "scintilla_innerfender_RL",
        "scintilla_innerfender_RR": "scintilla_innerfender_RR",
        "scintilla_intake_5.0": "scintilla_intake_5.0_race",
        "wheel_R_5": "wheel_dreid_c70_19x11_R",
        "licenseplate_design_2_1": "",
        "scintilla_lettering_fascia_R": "scintilla_lettering_fascia_R",
        "scintilla_lettering_fender_L": "scintilla_lettering_fender_L",
        "digidash_screen_logic": "digidash_screen_logic_bng",
        "digidash_cells_top_bar": "digidash_cells_top_bar_rpm",
        "scintilla_licenseplate_R": "scintilla_licenseplate_R",
        "scintilla_lip_F": "scintilla_lip_F",
        "digidash_cells_top_left_widget": "digidash_cells_top_left_wheelPressure",
        "scintilla_mirror_R": "scintilla_mirror_R",
        "scintilla_mod": ""}
    vars = {
        # Brakes
        "$brakestrength": 1,  # Brake force multiplier 60-100%
        "$brakebias": 0.55,  # Front/rear brake bias 0-100%

        # Chassis
        "$ffbstrength": 1,  # Setup-specific force feedback multiplier @100% 50-150
        "$spoiler_angle_R": 10,  # Rear wing angle, degrees 8-20
        "$fuel_R": 40,  # Right fuel volume L 0-40
        "$fuel_L": 40,  # Left fuel volume L 0-40

        # Differentials
        "$lsdpreload_F": 100,  # Pre-load torque N/m 0-500
        "$lsdlockcoefrev_F": 0,  # Coast lock rate % 0-100
        "$lsdlockcoef_F": 0.15,  # Power lock rate @ 25% 0-100
        "$finaldrive_F": 4.01,  # Final drive gear ratio 2-6
        "$lsdpreload_R": 100,  # Pre-load torque N/m 0-250
        "$lsdlockcoef_R": 0.15,  # Power lock rate @ 37% 0-100
        "$lsdlockcoefrev_R": 0,  # Coast lock rate % 0-100
        "$finaldrive_R": 4.01,  # Final drive gear ratio 2-6

        # Wheel alignment
        "$camber_F": 0.975,  # Camber @ -50%
        "$camber_R": 0.965,  # Camber @ -70%  -100-100
        "$caster_F": 1,  # Caster adjust  @ 0% -100-100. No rear caster adjust
        "$toe_F": 0.9796,  # @ 68%  -100-100
        "$toe_R": 0.984,  # @ -32%  -100-100
        "$steer_center_F": 0,  # Toe left/right trim @0% 0-100 (range -0.002-0.002)

        # Transaxle
        "$gear_1": 2.99,
        "$gear_2": 2.23,
        "$gear_3": 1.76,
        "$gear_4": 1.47,
        "$gear_5": 1.23,
        "$gear_6": 0.96,
        "$gear_R": 2.85,

        # Engine
        "$revLimiterCutTime": 0.1,  # RPM limit cut time s 0.01-0.5
        "$revLimiterRPM": 8350,  # RPM limit, 4500-10500

        # Suspension
        "$arb_spring_F": 75000,  # Ant-roll spring rate N/m 30000-150000
        "$spring_F_rally": 105000,  # Spring rate N/m 50000-200000
        "$springheight_F_rally": 0,  # Spring height m -0.04-0.08
        "$damp_bump_F_rally": 6800,  # Bump damping N/m/s 500-7500
        "$damp_bump_F_fast_rally": 4500,  # Fast Bump damping N/m/s 500-7500
        "$damp_rebound_F_rally": 8900,  # Rebound damping N/m/s 500-10000
        "$damp_rebound_F_fast_rally": 7500,  # Fast rebound damping N/m/s 500-10000
        "$arb_spring_R": 100000,  # Ant-roll spring rate N/m 15000-100000
        "$springheight_R_rally": 0,  # Spring height m -0.04 - 0.08
        "$spring_R_rally": 155000,  # Spring rate N/m 50000-250000
        "$damp_bump_R_fast_rally": 10200,  # Bump damping N/m/s 2500-15000
        "$damp_rebound_R_fast_rally": 22000,  # Fast rebound damping N/m/s 4500-25000
        "$damp_rebound_R_rally": 22000,  # Rebound damping N/m/s 4500-25000
        "$damp_bump_R_rally": 12500,  # Bump damping N/m/s 2500-15000

        # Wheels
        "$tirepressure_F": 28,  # Tire pressure psi 0-50
        "$trackoffset_F": -0.01,  # Wheel offset m -0.01-0.05
        "$tirepressure_R": 27,  # Tire pressure psi 0-50
        "$trackoffset_R": 0.025,  # Wheel offset m -0.01-0.05

        # Transfer case
        "$splitshaft_minlock": 0,  # Minimum lock % 0-20%
        "$splitshaft_torque": 600,  # Maximum torque N-m 0-1000
        "$splitshaft_stiffness": 0.0902,  # Locking rate (?) @39% 0-100%
        "$splitshaft_threshold": 16,  # Slip threshold % 0-40
    }
    paints = [
        {
            "roughness": 0.36,
            "clearcoat": 0.77,
            "clearcoatRoughness": 0.03,
            "baseColor": [0.88, 0, 0, 2],
            "metallic": 0.86
        },
        {
            "roughness": 0.36,
            "clearcoat": 0.77,
            "clearcoatRoughness": 0.03,
            "baseColor": [0.65, 0.65, 0.65, 1.2],
            "metallic": 0.86
        },
        {
            "roughness": 0.36,
            "clearcoat": 0.77,
            "clearcoatRoughness": 0.03,
            "baseColor": [1, 0.69, 0.03, 1.2],
            "metallic": 0.86
        }
    ]
