cmake_minimum_required(VERSION 3.5)

project(fMRSI)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "http://slicer.org/slicerWiki/index.php/Documentation/Nightly/Extensions/fMRSI")
set(EXTENSION_CATEGORY "MACBioIDI")
set(EXTENSION_CONTRIBUTORS "Francisco Marcano (Universidad de La Laguna)")
set(EXTENSION_DESCRIPTION "fMRSI Extension - MACBioIDI Project 2017-2020")
set(EXTENSION_ICONURL "http://www.example.com/Slicer/Extensions/fMRSI.png")
set(EXTENSION_SCREENSHOTURLS "http://www.example.com/Slicer/Extensions/fMRSI/Screenshots/1.png")
set(EXTENSION_DEPENDS "NA") # Specified as a space separated string, a list or 'NA' if any

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(PFileParser)
add_subdirectory(CFileParser)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
