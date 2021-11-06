

def checkOutputValues(output_dict, aircraftInfo: object):
    if output_dict['range_all'] < 0:
        print('Range: ', output_dict['range_all'])
        # raise ValueError("Negative Range All Value")

    # if output_dict['deflection_cruise_elevator'] < 0:
    #     print('deflection_cruise_elevator: ', output_dict['deflection_cruise_elevator'])

    # if output_dict['cruiseRange'] > 100:
    #     print(f"Cruise range: {output_dict['cruiseRange']}")
    #     print(f"Variables Optimization: {aircraftInfo.optimizationVariables}")