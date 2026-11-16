# gdsfactory Component Catalog

Full catalog: https://gdsfactory.github.io/gdsfactory/components.html

## Waveguides
- `straight(length, cross_section)` - straight waveguide
- `straight_array(n, spacing, length)` - parallel waveguides
- `straight_heater_metal(length, heater_width)` - waveguide with metal heater
- `straight_heater_doped_rib()` - doped rib heater
- `straight_heater_meander()` - meandered heater
- `straight_pin(length)` - PIN phase shifter
- `straight_pn(length)` - PN phase shifter
- `wire_straight()` - electrical wire
- `wire_corner()` - 90-degree wire corner
- `crossing()` - waveguide crossing
- `crossing45()` - 45-degree crossing

## Bends
- `bend_euler(radius, angle, cross_section)` - Euler/adiabatic bend
- `bend_circular(radius, angle)` - circular arc bend
- `bend_s(size, cross_section)` - S-bend (size=(dx,dy))
- `bend_euler_s()` - S-bend with Euler curves
- `bezier(control_points)` - Bezier curve bend
- `bend_euler_all_angle()` - all-angle Euler bend
- `bend_circular_all_angle()` - all-angle circular bend

## MMIs (Multimode Interference)
- `mmi1x2(width_mmi, length_mmi, gap_mmi)` - 1x2 splitter
- `mmi2x2(width_mmi, length_mmi, gap_mmi)` - 2x2 coupler
- `mmi(inputs, outputs, width_mmi, length_mmi)` - generic NxM MMI
- `mmi_tapered()` - tapered MMI
- `mmi_90degree_hybrid()` - 90-degree hybrid for coherent detection
- `mmi1x2_with_sbend()` - MMI with S-bend outputs
- `mmi2x2_with_sbend()` - MMI with S-bend outputs

## Couplers
- `coupler(gap, length, dy)` - directional coupler
- `coupler_ring(gap, radius, length_x)` - ring bus coupler
- `coupler90(gap, radius)` - 90-degree coupler
- `coupler_adiabatic()` - adiabatic coupler
- `coupler_asymmetric()` - asymmetric coupler
- `coupler_bent()` - bent coupler
- `coupler_broadband()` - broadband coupler
- `coupler_full(coupling_length, gap)` - full coupler (4 ports)
- `coupler_straight(length, gap)` - straight coupling section

## MZIs (Mach-Zehnder Interferometers)
- `mzi(delta_length, splitter, combiner)` - basic MZI
- `mzi_phase_shifter(delta_length)` - MZI with phase shifter
- `mzi_pin()` - MZI with PIN shifter
- `mzi1x2_2x2()` - 1x2 split, 2x2 combine
- `mzi2x2_2x2_phase_shifter()` - 2x2 with phase control
- `mzm()` - Mach-Zehnder modulator
- `mzi_lattice(coupler_lengths, delta_lengths)` - lattice filter

## Rings
- `ring_single(gap, radius, length_x)` - single bus ring
- `ring_double(gap, radius)` - add-drop ring (dual bus)
- `ring_single_heater(gap, radius)` - thermally tuned ring
- `ring_double_heater()` - dual bus with heater
- `ring_single_pn()` - PN junction ring modulator
- `ring_crow(gaps, radii)` - coupled resonator optical waveguide
- `disk(radius)` - disk resonator
- `disk_heater()` - disk with heater

## Grating Couplers
- `grating_coupler_elliptical(polarization, taper_length)` - elliptical GC
- `grating_coupler_rectangular(n_periods, period, fill_factor)` - rectangular GC
- `grating_coupler_dual_pol()` - dual polarization GC
- `grating_coupler_array(n, pitch)` - array of GCs
- `grating_coupler_tree(n)` - tree-connected GC array
- `grating_coupler_loss_fiber_array()` - GC loss test structure

## Tapers
- `taper(length, width1, width2)` - linear width taper
- `taper_adiabatic()` - adiabatic taper
- `taper_cross_section(cross_section1, cross_section2, length)` - XS transition
- `taper_parabolic()` - parabolic taper
- `taper_strip_to_ridge()` - strip to ridge transition
- `taper_sc_nc()` - Si to SiN transition
- `taper_nc_sc()` - SiN to Si transition

## Filters
- `awg(arms, free_propagation_length)` - arrayed waveguide grating
- `dbr(n_periods, period)` - distributed Bragg reflector
- `dbr_tapered()` - tapered DBR
- `loop_mirror()` - Sagnac loop mirror
- `mode_converter()` - waveguide mode converter
- `polarization_splitter_rotator()` - PSR

## Spirals & Delay Lines
- `spiral(length)` - compact spiral
- `spiral_double()` - double spiral
- `spiral_racetrack(straight_length, n_loops)` - racetrack spiral
- `spiral_inductor()` - RF inductor spiral
- `delay_snake(length, n_loops)` - serpentine delay

## Pads & Electrical
- `pad(size)` - single bond pad
- `pad_array(columns, rows, pitch)` - pad array
- `pad_gs()` - ground-signal probe pad
- `pad_gsg()` - GSG probe pad
- `pad_rectangular()` - rectangular pad
- `bump_pad()` - flip-chip bump pad
- `resistance_meander()` - meander resistor
- `interdigital_capacitor()` - IDC
- `inductor()` - planar inductor

## Vias
- `via(size, spacing, layer)` - single via
- `via_stack(size, layers)` - multi-layer via
- `via_chain(num_vias)` - via chain test structure
- `via_stack_m1_m3()` - M1 to M3 via stack
- `via_stack_m1_mtop()` - M1 to top metal
- `via_circular()` - circular via array

## Quantum & Superconducting
- `transmon(pocket_width, pocket_height)` - transmon qubit
- `transmon_circular()` - circular transmon
- `flux_qubit()` - flux qubit
- `resonator_cpw(length)` - CPW resonator
- `resonator_quarter_wave()` - quarter-wave resonator
- `coupler_capacitive()` - capacitive coupler
- `coupler_tunable()` - tunable coupler
- `snspd()` - superconducting nanowire SPD
- `hline()` - superconducting hairpin line
- `optimal_90deg()` - optimized 90-degree SC bend
- `optimal_hairpin()` - optimized hairpin
- `ytron_round()` - yTron device

## Shapes & Primitives
- `rectangle(size, layer)` - rectangle
- `circle(radius, layer)` - circle (polygonal approximation)
- `cross(length, width, layer)` - cross/plus
- `L(width, size)` - L-shape
- `C(width, size)` - C-shape
- `ellipse(radii, layer)` - ellipse
- `hexagon(side_length)` - hexagon
- `octagon(side_length)` - octagon
- `regular_polygon(sides, side_length)` - N-gon
- `triangle(x, xtop, y)` - triangle/trapezoid

## Text
- `text(text, size, layer)` - polygon text
- `text_freetype(text, size, font)` - FreeType rendered text
- `text_klayout(text, size)` - KLayout font text
- `text_rectangular(text, size)` - simple rectangular font

## Die & Packaging
- `die(size, street_width)` - die outline with marks
- `die_with_pads()` - die with bond pad frame
- `seal_ring(size)` - seal ring around die
- `wafer()` - full wafer layout
- `align_wafer()` - wafer alignment marks

## Test & Verification Structures
- `cutback_bend90(n_bends)` - bend loss test
- `cutback_splitter(n_splits)` - splitter loss test
- `greek_cross()` - sheet resistance test
- `resistance_meander()` - resistance test
- `litho_calipers()` - lithography calibration
- `verniers()` - layer alignment verniers
- `cdsem_all()` - CD-SEM structures

## Containers & Combinators
- `array(component, columns, rows, spacing)` - component array
- `splitter_tree(coupler, n_levels)` - binary splitter tree
- `switch_tree(n_levels)` - optical switch tree
- `component_sequence(sequence, symbol_to_component)` - sequenced layout
- `extend_ports(component, length)` - extend all ports
- `add_termination(component, terminator)` - terminate unused ports
