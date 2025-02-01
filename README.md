DIY-Nabra KiCAD footprint library
=================================

Peter Blasser makes beautiful and esoteric electronic instruments under the 
[Ciat-Lonbarde](https://www.ciat-lonbarde.net/ciat-lonbarde/index.html) brand name.

He has also published a series of DIY circuits intended to be built on a paper and 
cardboard sandwich called a paper circuit.  A summary of his paper circuits can be
found [here](https://www.ciat-lonbarde.net/ciat-lonbarde/TIMARACURRICULUM/TIMARATERIALS/cirques/index.html).
They contain an assortment of almost hieroglyphic like symbols which, coupled
with their non-orthogonal layouts, produce circuits that are artworks in themselves.

The majority of these paper circuits can be downloaded in a combined zip file from
[here](https://www.ciat-lonbarde.net/ciat-lonbarde/TIMARACURRICULUM/TIMARATERIALS/cirques/papers.zip).
The files in the zip are in the [Osmond PCB](https://www.osmondpcb.com) file format,
a Mac only application that is rather old and not supported on newer Macs, or Windows.

Ciat-Lonbarde DIY has a sizeable and enthusiastic on-line fanbase who have transferred
the paper circuits to PCBs, to make them easier to build.  Others have expanded on
the original circuits, or made their own circuits inspired by Peter's works.  The
unorthodox, yet aesthetic, symbols and layout of the circuits also has their 
admirers and a number of synth DIY enthusiasts have laid out their own circuits in
a manner similar to Peter's.

To encourage and support these enthusiasts and, mainly, as I am one of them, I spent
a typically UK winter wet Sunday afternoon writing a Python script to convert the 
component footprint symbols used in the Osmond PCB versions of the Ciat-Lonbarde 
paper circuits to [KiCAD](https://www.kicad.org) footprint symbols.  This repository is 
the product of that afternoon.  It contains:

* The KiCAD footprint library: `diy-nabra.pretty`
* The Python conversion script I wrote: `conversion-script/osm-to-kicad.py`
* The Osmond PCB footprint library I exported from Osmond PCB: `conversion-script/cl_osmond_library.osm`
* An example KiCAD project using the footprints: `3-roll/3-roll.kicad_pro`.  
This is a recreation of the 3-Roll circuit from Rollz-5 in KiCAD.  I have laid it 
out starting with the schematic.  I choose this as it is the simplest of all 
the paper circuits.
* A KiCAD project with all the footprints that I used to generate the image below:

![diy-nabra-display](nabra-display/nabra-display.png)

How to use
----------

* Clone the repo from GitHub: ```git clone```
    * or download the zipfile from:
* In the KiCAD PCB editor (`pcbnew`) go to `Preferences->Manage Footprint Libraries...`
    * Click the folder icon beneath the list of footprint libraries to add a new library from a directory
    * Navigate to the `diy-nabra.pretty` directory in the `NabraFootprints` directory that you cloned or expanded the zipfile into.
    * Click `Open`
* You should now see the `diy-nabra` Nickname and path in the list of footprints.