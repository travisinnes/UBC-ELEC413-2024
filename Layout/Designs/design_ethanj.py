from pya import *

 
def design_ethanj(cell, cell_y, inst_wg1, inst_wg2, inst_wg3, waveguide_type):
    
    # load functions
    from SiEPIC.scripts import connect_pins_with_waveguide, connect_cell
    ly = cell.layout()
    library = ly.technology().name

    cell_taper = ly.create_cell('ebeam_taper_350nm_2000nm_te1310', library)
    if not cell_taper:
        raise Exception ('Cannot load taper cell; please check the script carefully.')

    #####
    # designer circuit:

    # Create a physical text label so we can see under the microscope
    # How do we find out the PCell parameter variables?
    '''
    c = ly.create_cell('TEXT','Basic')
    [p.name for p in c.pcell_declaration().get_parameters() if c.is_pcell_variant]
    c.delete()
    '''
    # returns: ['text', 'font_name', 'layer', 'mag', 'inverse', 'bias', 'cspacing', 'lspacing', 'eff_cw', 'eff_ch', 'eff_lw', 'eff_dr', 'font']
    from SiEPIC.utils import get_technology_by_name
    TECHNOLOGY = get_technology_by_name(library)
    cell_text = ly.create_cell('TEXT', "Basic", {
        'text':cell.name,
        'layer': TECHNOLOGY['M1'],
        'mag': 30,
         })
    if not cell_text:
        raise Exception ('Cannot load text label cell; please check the script carefully.')
    cell.insert(CellInstArray(cell_text.cell_index(), Trans(Trans.R0, 25000,125000)))                

    # load the cells from the PDK
    # choose appropriate parameters
    cell_bragg = ly.create_cell('ebeam_pcell_bragg_grating', library, {
        'number_of_periods': 10,
        'grating_period': 0.293,
        'corrugation_width': 0.07,
        'wg_width': 0.350,
        'sinusoidal': False})
    if not cell_bragg:
        raise Exception ('Cannot load Bragg grating cell; please check the script carefully.')

    #cell_taper = ly.create_cell('ebeam_pcell_taper', library, {
    #    'wg_width1': 0.350,
    #    'wg_width2': 0.385,
    #        })
    #if not cell_taper:
    #    raise Exception ('Cannot load taper cell; please check the script carefully.')

    # instantiate y-branch (attached to input waveguide)
    inst_y1 = connect_cell(inst_wg1, 'opt2', cell_y, 'opt2')

    #inst_taper1 = connect_cell(inst_y1, 'opt1', cell_taper, 'pin1')
    
    # instantiate Bragg grating (attached to y branch)
    inst_bragg1 = connect_cell(inst_y1, 'opt1', cell_bragg, 'opt1')
    
    # instantiate taper from bragg1 to cavity
    #inst_taper1 = connect_cell(inst_bragg1, 'opt2', cell_taper, 'pin1')

    # instantiate taper from cavity to bragg2
    #inst_taper2 = connect_cell(inst_taper1, 'pin2', cell_taper, 'pin2')
    
    # Number of cavity waveguide loops
    n_trips = 5
    
    # instantiate Bragg grating (attached to the first Bragg grating)
    inst_bragg2 = connect_cell(inst_y1, 'opt1', cell_bragg, 'opt2')
    
    # move the Bragg grating to the right, and up
    inst_bragg2.transform(Trans(330000,18000*(2*n_trips)))

    #####
    # Waveguides for the two outputs:
    connect_pins_with_waveguide(inst_y1, 'opt3', inst_wg3, 'opt1', waveguide_type=waveguide_type)

    # instantiate taper from 350 nm waveguide y-branch to 385 nm Bragg grating
    #inst_taper4 = connect_cell(inst_bragg2, 'opt1', cell_taper, 'pin2')

    connect_pins_with_waveguide(inst_bragg2, 'opt1', inst_wg2, 'opt1', waveguide_type=waveguide_type)
    
    # Waveguide (borrowed from design_lukasc_6)
    connect_pins_with_waveguide(inst_bragg1, 'opt2', inst_bragg2, 'opt2', 
        waveguide_type='Si routing TE 1310 nm (compound waveguide)',
        turtle_A = [300,90,18,90,300,-90,18,-90]*n_trips )

    #try:
    #    connect_pins_with_waveguide(inst_taper1, 'pin2', inst_taper2, 'pin2', 
    #        waveguide_type='Strip TE 1310 nm, w=350 nm (core-clad)', 
    #        turtle_A = [330,90,18,90,350,-90,18,-90,350,90,18,90,350,-90,18,-90,310,90,18,90,310,-90,18,-90,310,90,18,90,310,-90,18,-90,310,90,18,90,310,-90,18,-90,310,90] )
    #except:    
    #    raise Exception ('Cannot make waveguide; please check the script carefully.')

    return inst_wg1, inst_wg2, inst_wg3