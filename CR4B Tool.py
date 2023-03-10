# Halo CR4B Tool - Completely Ready 4 Blender Tool
#Created by Plastered_Crab
bl_info = {
    "name": "CR4B Tool",
    "description": "An addon that aims to get Halo 3/ODST/Reach levels and objects as close to game accurate as possible with one click",
    "author": "Add-on by Plastered_Crab. Shaders made by Chiefster with help from Soulburnin",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar > CR4B Tool",
    "warning": "",
    "category": "Object"
}

import bmesh
import bpy
import subprocess
import pathlib
import math
import time
import os
import re
import struct
import ntpath
import sys
from bpy_extras import view3d_utils
import mathutils
from mathutils import Vector
import os.path
from mathutils import Matrix
# for some profiling
from time import perf_counter
import cProfile
import pstats

#Dependant modules
#import scipy
#import pillow
import numpy as np
#from PIL import Image
#import py360convert

#from bitstring import ConstBitStream


#LOOPS THROUGH ALL OBJECTS IN BLEND FILE
# if bpy.context.selected_objects == []:
        # print('selected:')
        # for obj in bpy.context.scene.objects: 
            # print(obj.name, obj, obj.type)
            # if obj.type == 'MESH': 
                # print("&gt;&gt;&gt;&gt;", obj.name)


                    #[HARD CODED DATA AREA]#





#Start of the program
def Start_CR4B_Tool():


    #DEPENDANCIES NEEDED
    # pip install cube2sphere  for python 3.0+
    # https://github.com/Xyene/cube2sphere

    # pip install py360convert  
    # https://github.com/sunset1995/py360convert

    #update the context.scene
    #bpy.context.scene.update()
    
    #MUST SPECIFY THE ROOT FOLDER OF YOUR TAGS FOR HALO 3 HERE!!!!!
    print("Drop Down option: " + bpy.context.scene.tag_dropdown)
    #Tag_Root = ""
    if(bpy.context.scene.tag_dropdown == "Halo 3"):
        print("Using Halo 3 Tags")
        Tag_Root = bpy.context.preferences.addons[__name__].preferences.halo3_tag_path 
        print("halo3_tag_path: " + bpy.context.preferences.addons[__name__].preferences.halo3_tag_path)
    elif (bpy.context.scene.tag_dropdown == "Halo 3: ODST"):
        print("Using Halo 3: ODST Tags")
        print("odst_tag_path: " + bpy.context.preferences.addons[__name__].preferences.odst_tag_path)
        Tag_Root = bpy.context.preferences.addons[__name__].preferences.odst_tag_path
    elif (bpy.context.scene.tag_dropdown == "Halo Reach"):
        print("Using Halo Reach Tags")
        print("reach_tag_path: " + bpy.context.preferences.addons[__name__].preferences.reach_tag_path)
        Tag_Root = bpy.context.preferences.addons[__name__].preferences.reach_tag_path
    else:
        print("Error with Tag option property")
             
    #MUST SPECIFY THE ROOT FOLDER OF YOUR MODELS YOU RIPPED (FROM DRIVE LETTER -> BASE FOLDER WHERE YOU EXPORT YOUR MODELS, TEXTURES, AND .BLEND FILES)
    Export_Root = bpy.context.preferences.addons[__name__].preferences.export_path
    #Export_Root = "C:/Users/jeffr/Downloads/H3 Material Tool/Test Objects"
    
      
    DEFAULT_BITMAP_DIR = "shaders/default_bitmaps/bitmaps/"
    IMAGE_EXTENSION = bpy.context.scene.image_format
    print(IMAGE_EXTENSION)
    Preferred_Blend = 'BLEND'    #Either 'BLEND' or 'HASHED'

    #################################
    #NODE GRAPH CUSTOMIZING VARIABLES
    #################################

    #end group node placement
    ALPHA_BLEND_HORIZONTAL_SPACING = 250
    ALPHA_TEST_HORIZONTAL_SPACING = 250
    ADDITIVE_GROUP_HORIZONTAL_SPACING = 250
    ADD_SHADER_HORIZONTAL_SPACING = 250

    #main group node placement
    ENVIRONMENT_GROUP_VERTICAL_SPACING = 250
    SELF_ILLUM_VERTICAL_SPACING = 250

    #texture group node placement
    TEXTURE_NODE_VERTICAL_PLACEMENT = 550              # vertical placement of the entire texture node groups
    TEXTURE_NODE_HORIZONTAL_PLACEMENT = 600            # horizontal placment of the entire texture node groups
    TEXTURE_GROUP_VERTICAL_SPACING = 120               # vertical spacing in-between each texture segment
    TEXTURE_MAPPING_HORIZONTAL_SPACING = 200           # horizontal spacing between the mapping node and the texture nodes
    ADDITIONAL_MIRROR_NODE_VERTICAL_SPACING = 100      # adds extra padding between each texture cluster when a mirror node is present
    TEXTURE_MIRROR_NODE_HORIZONTAL_SPACING = 200       # horizontal spacing between the mirror group and texture node
    TEXTURE_COORD_NODE_HORIZONTAL_SPACING = 200        # horizontal spacing between tex coordinate node and mapping node
    TEXTURE_NODE_W_GAMMA_HORIZONTAL_SPACING = 50       # horizontal placement of texture node when it has gamma
    TEXTURE_GAMMA_HORIZONTAL_PLACEMENT = 100           # horizontal placement of the gamma nodes



    #DEBUG VALUES
    debug_textures_values_found = 1              # show debug info for found/unfound texture types and values




    #some global variables
    DefaultNeeded = 0
    ShadersConnected = 0
    ShaderOutputCount = 0
    ShaderGroupList = []


    color_white_rgb = [1.00, 1.00, 1.00, 1.00]
    color_gray_rgb = [0.5, 0.5, 0.5, 1.00]
    color_black_rgb = [0.00, 0.00, 0.00, 1.00]

    class wrap_mode:
        option = 0
        bitmap_type = ""


    class function:
        tsgt_offset = 0x0
        option = 0 #function option
        range_toggle = False #off or on
        # periodic_option1 = 0
        # periodic_option2 = 0
        # transition_option1 = 0
        # transition_option2 = 0
        function_name = ""
        range_name = ""
        
        #main values
        time_period = 0.00
        main_min_value = 0.00
        main_max_value = 0.00
        
        #main values
        left_function_option = 0
        left_frequency_value = 0.00
        left_phase_value = 0.00
        left_min_value = 0.00
        left_max_value = 0.00
        left_exponent_value = 0.00
        
        #used when range is toggled on
        right_function_option = 0
        right_frequency_value = 0.00
        right_phase_value = 0.00
        right_min_value = 0.00
        right_max_value = 0.00
        right_exponent_value = 0.00
        
        #used when it is a color function
        color_option = 0  #the option used for the function
        color_1 = [0.00, 0.00, 0.00, 0.00]
        color_2 = [0.00, 0.00, 0.00, 0.00]
        color_3 = [0.00, 0.00, 0.00, 0.00]
        color_4 = [0.00, 0.00, 0.00, 0.00]
        

    class bitmap:
        name = ""
        directory = ""
        curve_option = 0
        width = 0
        height = 0
        type = ""
        has_scale_x = False
        has_scale_y = False
        has_scale_uniform = False
        has_translation_x = False
        has_translation_y = False
        translation_xy = [0.00, 0.00]
        scale_xy = [1.00, 1.00]
        scale_uniform = 1.00 #gets overritten by xy
        transform_type_list = []
        transform_list = []
        disabled = False
        wrap_option = 0  #3 - mirror uni   4 or 5 - mirror X    9 - mirrorY   13 - both XY
        

    class shader:
        name = ""
        directory = ""
        bitmap_count = 0
        
        #category options
        albedo_option = 0
        bump_mapping_option = 0
        alpha_test_option = 0
        specular_mask_option = 0
        material_model_option = 0
        environment_mapping_option = 0
        self_illumination_option = 0
        blend_mode_option = 0
        parallax_option = 0
        misc_option = 0
        
        #alpha used by type - dictated by alpha_test
        type_w_alpha = ""
        alpha_bitmap_dir = ""
        
        #scaling/colors/values
        albedo_blend = 0.00
        albedo_color = color_white_rgb #BGR 3 decimal values
        albedo_color_alpha = 1.00 #1 decimal
        bump_detail_coefficient = 1.00 #1 decimal
        env_tint_color = color_white_rgb #BGR 3 decimal values
        env_roughness_scale = 0.00
        self_illum_color = color_white_rgb #BGR 3 decimal values
        self_illum_intensity = 1.00                                 
        channel_a = color_white_rgb #BGR 3 decimal
        channel_a_alpha = 0.00
        channel_b = color_white_rgb #BGR 3 decimal
        channel_b_alpha = 0.00
        channel_c = color_white_rgb #BGR 3 decimal
        channel_c_alpha = 0.00
        color_medium = color_white_rgb #BGR 3 decimal
        color_medium_alpha = 0.00
        color_wide = color_white_rgb #BGR 3 decimal
        color_wide_alpha = 0.0
        color_sharp = color_white_rgb #BGR 3 decimal
        color_sharp_alpha = 0.00
        thinness_medium = 0.00
        thinness_wide = 0.00
        thinness_sharp = 0.00
        meter_color_on = color_white_rgb #BGR 3 decimal
        meter_color_off = color_white_rgb #BGR 3 decimal
        meter_value = 0.00
        primary_change_color_blend = 0.00
        height_scale = 0.00
        diffuse_coefficient = 1.00
        specular_coefficient = 0.00
        specular_tint = color_white_rgb #BGR 3 decimal
        fresnel_color = color_gray_rgb #BGR 3 decimal
        roughness = 0.40
        environment_map_specular_contribution = 0.00
        use_material_texture = 0.00 #0 to 1   False or True
        normal_specular_power = 10.00
        normal_specular_tint = color_white_rgb #BGR 3 decimal
        glancing_specular_power = 10.00
        glancing_specular_tint = color_white_rgb #BGR 3 decimal
        fresnel_curve_steepness = 5.00
        albedo_specular_tint_blend = 0.00
        fresnel_curve_bias = 0.00
        fresnel_coefficient = 0.1
        analytical_specular_contribution = 0.00
        
        #terrain stuff
          #categories  start 20 bytes after shaders/shaders in terrain_shader file
        blending_option = 0
        environment_map_option = 0
        material_0_option = 0
        material_1_option = 0
        material_2_option = 0
        material_3_option = 0
        
        #textures
        # blend_map
        
        # base_map_m_0
        # detail_map_m_0
        # bump_map_m_0
        # detail_bump_m_0
        
        # base_map_m_1
        # detail_map_m_1
        # bump_map_m_1
        # detail_bump_m_1
        
        # base_map_m_2
        # detail_map_m_2
        # bump_map_m_2
        # detail_bump_m_2   
        
        # base_map_m_3
        # detail_map_m_3
        # bump_map_m_3
        # detail_bump_m_3  
        
          #scaling/colors/values
        global_albedo_tint = 1.00
        
        diffuse_coefficient_m_0 = 1.00
        specular_coefficient_m_0 = 0.00
        specular_power_m_0 = 10.00
        specular_tint_m_0 = color_white_rgb
        fresnel_curve_steepness_m_0 = 5.00
        area_specular_contribution_m_0 = 0.50
        analytical_specular_contribution_m_0 = 0.50
        environment_specular_contribution_m_0 = 0.00
        albedo_specular_tint_blend_m_0 = 0.00
        
        diffuse_coefficient_m_1 = 1.00
        specular_coefficient_m_1 = 0.00
        specular_power_m_1 = 10.00
        specular_tint_m_1 = color_white_rgb
        fresnel_curve_steepness_m_1 = 5.00
        area_specular_contribution_m_1 = 0.50
        analytical_specular_contribution_m_1 = 0.50
        environment_specular_contribution_m_1 = 0.00
        albedo_specular_tint_blend_m_1 = 0.00
        
        diffuse_coefficient_m_2 = 1.00
        specular_coefficient_m_2 = 0.00
        specular_power_m_2 = 10.00
        specular_tint_m_2 = color_white_rgb
        fresnel_curve_steepness_m_2 = 5.00
        area_specular_contribution_m_2 = 0.50
        analytical_specular_contribution_m_2 = 0.50
        environment_specular_contribution_m_2 = 0.00
        albedo_specular_tint_blend_m_2 = 0.00
        
        diffuse_coefficient_m_3 = 1.00
        specular_coefficient_m_3 = 0.00
        specular_power_m_3 = 10.00
        specular_tint_m_3 = color_white_rgb
        fresnel_curve_steepness_m_3 = 5.00
        area_specular_contribution_m_3 = 0.50
        analytical_specular_contribution_m_3 = 0.50
        environment_specular_contribution_m_3 = 0.00
        albedo_specular_tint_blend_m_3 = 0.00 


        #halogram stuff
        warp_option = 0
        overlay_option = 0
        edge_fade_option = 0
        distortion_option = 0
        soft_fade_option = 0

        #used for default textures
        #texture reference offsets
        BaseMap_Offset = 0x0
        DetailMap_Offset = 0x0
        DetailMap2_Offset = 0x0
        DetailMap3_Offset = 0x0
        SpecularMaskTexture_Offset = 0x0
        ChangeColorMap_Offset = 0x0
        BumpMap_Offset = 0x0
        BumpDetailMap_Offset = 0x0
        EnvironmentMap_Offset = 0x0
        FlatEnvironmentMap_Offset = 0x0
        SelfIllumMap_Offset = 0x0
        SelfIllumDetailMap_Offset = 0x0
        
        #offset for Alpha_Test_Map
        AlphaTestMap_Offset = 0x0



        needed_bitmaps = []
        env_tint_color_offset_list = []
        bitmap_list = []      #list of bitmap class objects for each bitmap used by the shader
        function_list = []
        wrap_mode_list = []
        
        
        
    #some global variables
    ShaderList = []   #list of all shader information
    ShaderList_Index = 0
    Shader_Type = 0


    def Is_Bitmap_Disabled(ShaderItem, BitmapType):
        if (BitmapType == "base_map"): #if albedo option is off
            print("Albedo Option not disabling: base_map")
            return False
        elif (BitmapType == "detail_map"):
            if(ShaderItem.albedo_option == 2 or ShaderItem.albedo_option == 17): #if albedo option is off
                print("Albedo Option disabling: detail_map")
                return True
            else: 
                print("Albedo Option not disabling: detail_map")
                return False
        elif (BitmapType == "bump_map"):
            if (ShaderItem.bump_mapping_option == 0): #if bump map option is off
                print("Bump Mapping Option disabling: bump_map")
                return True
            else:
                print("Bump Mapping Option not disabling: bump_map")
                return False
        elif (BitmapType == "bump_detail_map"):
            if (ShaderItem.bump_mapping_option == 0 or ShaderItem.bump_mapping_option == 1): # if bump mapping option is off or set to standard
                print("Bump Mapping Option disabling: bump_detail_map")
                return True
            else:
                print("Bump Mapping Option not disabling: bump_detail_map not disabled")
                return False
        elif (BitmapType == "self_illum_map"):
            if (ShaderItem.self_illumination_option == 0): #if self_illum option is off
                print("Self Illum Option disabling: self_illum_map")
                return True
            else: #other options
                print("Self Illum Option not disabling: self_illum_map")
                return False
        elif (BitmapType == "self_illum_detail_map"):
            if (ShaderItem.self_illumination_option != 5 and ShaderItem.self_illumination_option != 10): #if self_illum option is not self_illum_detail or illum_detail_world_space_four_cc 
                print("Self Illum Option not disabling: self_illum_detail_map")
                return False
            else: #other options
                print("Self Illum Option disabling: self_illum_detail_map")
                return True
        elif (BitmapType == "environment_map"):
            if (ShaderItem.environment_mapping_option == 0): #if environment option is off
                print("Environment Option disabling: environment_map")
                return True
            else: #other options
                print("Environment Option not disabling: environment_map not disabled")
                return False
        else:
            print("Different Bitmap type trying to be handled")
       

    def get_ascii_string(file, offset, size):
        temp_string = ""
        SampleByte = ""
        ASCIIstring = []

        file.seek(offset)
        for pymat_copy in range(size):
            SampleByte = file.read(1).decode("UTF-8")
            ASCIIstring.append(SampleByte)
        
        ASCIIstring = ''.join(ASCIIstring)
        directory_string = ASCIIstring
        directory_string = directory_string
        #print("type: " + directory_string)
        return directory_string
       
    def get_before_type_offset(file, offset):
        directory_string = ""
        SampleByte = ""
        DirString = []

        file.seek(offset - 0x1)
        while not SampleByte == '\x00':   #while loop to run through the directory lists and build strings until it finds a null byte then saves it to an array
            SampleByte = file.read(1).decode("UTF-8")
            #print("SampleByte: " + SampleByte)
            if not SampleByte == '\x00':
                if SampleByte == '\\':
                    SampleByte = '/'
                file.seek(file.tell() - 0x2)
        
        return file.tell()


    #Get the directory from the .shader files and remove anything not needed
    def get_dir(file, offset):
        directory_string = ""
        SampleByte = ""
        DirString = []
        
        file.seek(offset)
        while not SampleByte == '\x00':   #while loop to run through the directory lists and build strings until it finds a null byte then saves it to an array
            SampleByte = file.read(1).decode("UTF-8")
            if not SampleByte == '\x00':
                if SampleByte == '\\':
                    SampleByte = '/'

                DirString.append(SampleByte)
        DirString = ''.join(DirString)
        directory_string = DirString
        directory_string = directory_string[:-4]
        return directory_string

    def has_value(file, offset):
        #has_function(file, offset)
        file.seek(offset + 0x2C) #skips 44 bytes from where it is told
        test_bytes = 0
        test_bytes = int.from_bytes(file.read(4), 'little')
        if (test_bytes == 1952936809): #if the next 4 bytes equal 'isgt' then there is no scaling or color values
            return False
        else:
            return True
            
    def median_rgba(FunctionIten):
        #mix colors to be half the rgb value
        temp_r = (FunctionItem.color_1[0] + FunctionItem.color_4[0]) / 2
        temp_g = (FunctionItem.color_1[1] + FunctionItem.color_4[1]) / 2
        temp_b = (FunctionItem.color_1[2] + FunctionItem.color_4[2]) / 2
        temp_a = (FunctionItem.color_1[3] + FunctionItem.color_4[3]) / 2
                        
        temp_rgba = []
        temp_rgba.append(temp_r)
        temp_rgba.append(temp_g)
        temp_rgba.append(temp_b)
        temp_rgba.append(temp_a)
        
        return temp_rgba
                        
                           
            
            
    def has_function(file, offset):
        file.seek(offset + 0x50) #skip 80 bytes from offset to where isgt might be
        test_isgt = 0
        test_empty = 0
        test_after_adgt = 0
        test_isgt = int.from_bytes(file.read(4), 'little')
        test_empty = int.from_bytes(file.read(8), 'little')
        
        #print("inside has_function()")
        #print("isgt: " + str(test_isgt))
        
        #seek to test area 8 bytes after adgt
        file.seek(test_find(file.tell(), file, "adgt") + 0x8)
        
        test_after_adgt = int.from_bytes(file.read(2), 'little') #if it is 32 then function doesn't exist
        #print(" test after adgt value: " + str(test_after_adgt))
        
        if (test_isgt == 1952936809): #if isgt is there
            #print("  passed isgt test")
            if(test_after_adgt != 32):  #removed (test_empty != 0)  from this
                #print("There is probably a function here!")
                return True
            else:
                #print("Probably no function here")
                return False

    #find and return offset of the beginning of an ASCII string
    def get_ASCII_offset(file, offset_start, ASCII): 
        ASCII_byte = bytes(ASCII, 'utf-8')
        file = open(ShaderPath, "rb")
        file_read = file.read()
        
        return file_read.find(ASCII_byte, offset_start)


    #builds function object and returns object
    def get_function_color(file, offset, function_object):
        print("")
        #ADD CODE HERE LATER

    #builds function object and return that object
    def get_function_data(file, offset, function_object):
        #clear function object
        function_object.tsgt_offset = 0x0
        function_object.option = 0
        function_object.range_toggle = False
        function_object.function_name = ""
        function_object.range_name = ""
        function_object.time_period = 0.00
        function_object.main_min_value = 0.00
        function_object.main_max_value = 0.00
        function_object.left_function_option = 0
        function_object.left_frequency_value = 0.00
        function_object.left_phase_value = 0.00
        function_object.left_min_value = 0.00
        function_object.left_max_value = 0.00
        function_object.left_exponent_value = 0.00
        function_object.right_function_option = 0
        function_object.right_frequency_value = 0.00
        function_object.right_phase_value = 0.00
        function_object.right_min_value = 0.00
        function_object.right_max_value = 0.00
        function_object.right_exponent_value = 0.00
        
        function_name_offset = 0x0 #offset of the start of the function name
        range_name_offset = 0x0 #offset of the start of the range name
        tsgt_offset = 0x0 #offset of right after the potential range name of the function
        range_name_length = 0
        
        #get time_period
        file.seek(offset + 0x2C) #skip 44 bytes to get time_period
        function_object.time_period = struct.unpack('f', file.read(4))[0] #grab the time_period
        
        #get function_name and offset
        file.seek(offset + 0x5C) #skip 92 bytes to get name of function
        function_name_offset = file.tell() #sets the range_name_offset
        function_object.function_name = get_dir(file, function_name_offset) #get name of function
        
        #get range_name_offset
        range_name_offset = file.seek(function_name_offset + len(function_object.function_name) + 0xC) #jump to end of function name and then 12 bytes
        
        #store tsgt_offset
        function_object.tsgt_offset = get_ASCII_offset(file, range_name_offset, "tsgt") #get offset of the start of 'tsgt' right after name of range
        
        #get name of range name
        range_name_length = function_object.tsgt_offset - range_name_offset #gets length of range name
        file.seek(range_name_offset) #seek to start of range name
        range_name_bytes = file.read(range_name_length)
        
        function_object.range_name = range_name_bytes.decode('UTF-8')
        
        #start at tsgt_offset + 24 bytes
        file.seek(function_object.tsgt_offset + 0x18)
        
        #grab function option
        function_object.option = int.from_bytes(file.read(1), 'little')
        
        temp_toggle = int.from_bytes(file.read(1), 'little')
        #grab range_toggle
        if (temp_toggle == 37): #toggle on
            function_object.range_toggle == True
        elif (temp_toggle == 36): #toggle off
            function_object.range_toggle == False
        else:
            print("Function toggle data issue")
            
        
        #jump to tsgt_offset + 28 bytes 
        file.seek(function_object.tsgt_offset + 0x1C)
        
        #grab both main min and max values
        function_object.main_min_value = struct.unpack('f', file.read(4))[0]
        function_object.main_max_value = struct.unpack('f', file.read(4))[0]

        #grab certain data depending on each option
        if(function_object.option != 1 and function_object.option != 8): #option = basic or curve
            if(function_object.option == 3): #option = periodic
                #jump to tsgt_offset + 56 bytes
                file.seek(function_object.tsgt_offset + 0x38) 
            
                #store left function option
                function_object.left_function_option = int.from_bytes(file.read(1), 'little')

                #jump to tsgt_offset + 60 bytes
                file.seek(function_object.tsgt_offset + 0x3C)
                
                #grab left values
                function_object.left_frequency_value = struct.unpack('f', file.read(4))[0]
                function_object.left_phase_value = struct.unpack('f', file.read(4))[0]
                function_object.left_min_value = struct.unpack('f', file.read(4))[0]
                function_object.left_max_value = struct.unpack('f', file.read(4))[0]
                
                #jump to tsgt_offset + 76 bytes
                file.seek(function_object.tsgt_offset + 0x4C)
                
                #grab Right values
                function_object.right_function_option = int.from_bytes(file.read(1), 'little')
                
                #jump to tsgt_offset + 80 bytes
                file.seek(function_object.tsgt_offset + 0x54)
                
                #grab right values
                function_object.right_frequency_value = struct.unpack('f', file.read(4))[0]
                function_object.right_phase_value = struct.unpack('f', file.read(4))[0]
                function_object.right_min_value = struct.unpack('f', file.read(4))[0]
                function_object.right_max_value = struct.unpack('f', file.read(4))[0]
         
                #repeat again for copy of all values?
                
            elif(function_object.option == 9): #option = exponent
                #jump to tsgt_offset + 56 bytes
                file.seek(function_object.tsgt_offset + 0x38)
                
                #grab left values
                function_object.left_min_value = struct.unpack('f', file.read(4))[0]
                function_object.left_max_value = struct.unpack('f', file.read(4))[0]
                function_object.left_exponent_value = struct.unpack('f', file.read(4))[0]
                
                #grab right values
                function_object.right_min_value = struct.unpack('f', file.read(4))[0]
                function_object.right_max_value = struct.unpack('f', file.read(4))[0]
                function_object.right_exponent_value = struct.unpack('f', file.read(4))[0]
                
                #repeat again for copy of all values?
                
            elif(function_object.option == 2): #option = transition
                
                #jump to tsgt_offset + 56 bytes
                file.seek(function_object.tsgt_offset + 0x38) 
            
                #store left function option
                function_object.left_function_option = int.from_bytes(file.read(1), 'little')

                #jump to tsgt_offset + 60 bytes
                file.seek(function_object.tsgt_offset + 0x3C)
                
                #grab left values
                function_object.left_min_value = struct.unpack('f', file.read(4))[0]
                function_object.left_max_value = struct.unpack('f', file.read(4))[0]
                
                #jump to tsgt_offset + 68 bytes
                file.seek(function_object.tsgt_offset + 0x44)
                
                #grab Right values
                function_object.right_function_option = int.from_bytes(file.read(1), 'little')
                
                #jump to tsgt_offset + 72 bytes
                file.seek(function_object.tsgt_offset + 0x48)
                
                #grab right values
                function_object.right_min_value = struct.unpack('f', file.read(4))[0]
                function_object.right_max_value = struct.unpack('f', file.read(4))[0]
         
                #repeat again for copy of all values?
                
            else:
                print("Function Option issue")
            
        return function_object


    #for color function data
    def get_color_function_data(file, offset, function_object):
        #clear function object
        function_object.tsgt_offset = 0x0
        function_object.option = 0
        function_object.range_toggle = False
        function_object.function_name = ""
        function_object.range_name = ""
        function_object.time_period = 0.00
        function_object.main_min_value = 0.00
        function_object.main_max_value = 0.00
        function_object.left_function_option = 0
        function_object.left_frequency_value = 0.00
        function_object.left_phase_value = 0.00
        function_object.left_min_value = 0.00
        function_object.left_max_value = 0.00
        function_object.left_exponent_value = 0.00
        function_object.right_function_option = 0
        function_object.right_frequency_value = 0.00
        function_object.right_phase_value = 0.00
        function_object.right_min_value = 0.00
        function_object.right_max_value = 0.00
        function_object.right_exponent_value = 0.00
        
        
        #add color rgb defaults
        function_object.color_option = 0
        function_object.color_1 = [0.00, 0.00, 0.00, 0.00]
        function_object.color_2 = [0.00, 0.00, 0.00, 0.00]
        function_object.color_3 = [0.00, 0.00, 0.00, 0.00]
        function_object.color_4 = [0.00, 0.00, 0.00, 0.00]
        
        #temp color values
        temp_color_R = 0.00
        temp_color_G = 0.00
        temp_color_B = 0.00
        
        function_name_offset = 0x0 #offset of the start of the function name
        range_name_offset = 0x0 #offset of the start of the range name
        tsgt_offset = 0x0 #offset of right after the potential range name of the function
        range_name_length = 0
        
        #get time_period
        file.seek(offset + 0x2C) #skip 44 bytes to get time_period
        function_object.time_period = struct.unpack('f', file.read(4))[0] #grab the time_period
        
        #get function_name and offset
        file.seek(offset + 0x5C) #skip 92 bytes to get name of function
        function_name_offset = file.tell() #sets the range_name_offset
        function_object.function_name = get_dir(file, function_name_offset) #get name of function
        
        #get range_name_offset
        range_name_offset = file.seek(function_name_offset + len(function_object.function_name) + 0xC) #jump to end of function name and then 12 bytes
        
        #store tsgt_offset
        function_object.tsgt_offset = get_ASCII_offset(file, range_name_offset, "tsgt") #get offset of the start of 'tsgt' right after name of range
        
        #get name of range name
        range_name_length = function_object.tsgt_offset - range_name_offset #gets length of range name
        file.seek(range_name_offset) #seek to start of range name
        range_name_bytes = file.read(range_name_length)
        
        function_object.range_name = range_name_bytes.decode('UTF-8')
        
        print("------Function Found-------")
        
        #start at tsgt_offset + 24 bytes
        file.seek(function_object.tsgt_offset + 0x18)
        
        #grab function option
        function_object.option = int.from_bytes(file.read(1), 'little')
        
        temp_toggle = int.from_bytes(file.read(1), 'little')
        #grab range_toggle
        if (temp_toggle == 37): #toggle on
            function_object.range_toggle == True
        elif (temp_toggle == 36): #toggle off
            function_object.range_toggle == False
        else:
            print("Function toggle data issue")
            
        #grab color function option
        function_object.color_option = int.from_bytes(file.read(1), 'little')  
        print("color_option: " + get_color_option(function_object.color_option))
        
        #jump to tsgt_offset + 28 bytes 
        file.seek(function_object.tsgt_offset + 0x1C)
        
        
        #grab color 1
        temp_color_B = float(int.from_bytes(file.read(1), 'little')) / 255
        temp_color_G = float(int.from_bytes(file.read(1), 'little')) / 255
        temp_color_R = float(int.from_bytes(file.read(1), 'little')) / 255
        file.seek(file.tell() + 0x1)
        
        #store color 1
        function_object.color_1.clear() #clear the list to empty it
        function_object.color_1.append(temp_color_R)
        function_object.color_1.append(temp_color_G)
        function_object.color_1.append(temp_color_B)
        function_object.color_1.append(1.00)
        print("color 1: " + str(function_object.color_1))
        
        
        #grab color 2
        temp_color_B = float(int.from_bytes(file.read(1), 'little')) / 255
        temp_color_G = float(int.from_bytes(file.read(1), 'little')) / 255
        temp_color_R = float(int.from_bytes(file.read(1), 'little')) / 255
        file.seek(file.tell() + 0x1)
        
        #store color 2
        function_object.color_2.clear() #clear the list to empty it
        function_object.color_2.append(temp_color_R)
        function_object.color_2.append(temp_color_G)
        function_object.color_2.append(temp_color_B)
        function_object.color_2.append(1.00)
        print("color 2: " + str(function_object.color_2))
        
        
        #grab color 3
        temp_color_B = float(int.from_bytes(file.read(1), 'little')) / 255
        temp_color_G = float(int.from_bytes(file.read(1), 'little')) / 255
        temp_color_R = float(int.from_bytes(file.read(1), 'little')) / 255
        file.seek(file.tell() + 0x1)
        
        #store color 3
        function_object.color_3.clear() #clear the list to empty it
        function_object.color_3.append(temp_color_R)
        function_object.color_3.append(temp_color_G)
        function_object.color_3.append(temp_color_B)
        function_object.color_3.append(1.00)
        print("color 3: " + str(function_object.color_3))

        #grab color 4
        temp_color_B = float(int.from_bytes(file.read(1), 'little')) / 255
        temp_color_G = float(int.from_bytes(file.read(1), 'little')) / 255
        temp_color_R = float(int.from_bytes(file.read(1), 'little')) / 255
        file.seek(file.tell() + 0x1)
        
        #store color 4
        function_object.color_4.clear() #clear the list to empty it
        function_object.color_4.append(temp_color_R)
        function_object.color_4.append(temp_color_G)
        function_object.color_4.append(temp_color_B)
        function_object.color_4.append(1.00)
        print("color 4: " + str(function_object.color_4))
      
        
        #grab certain data depending on each option
        if(function_object.option != 1 and function_object.option != 8): #option = basic or curve
            if(function_object.option == 3): #option = periodic
                #jump to tsgt_offset + 56 bytes
                file.seek(function_object.tsgt_offset + 0x38) 
            
                #store left function option
                function_object.left_function_option = int.from_bytes(file.read(1), 'little')

                #jump to tsgt_offset + 60 bytes
                file.seek(function_object.tsgt_offset + 0x3C)
                
                #grab left values
                function_object.left_frequency_value = struct.unpack('f', file.read(4))[0]
                function_object.left_phase_value = struct.unpack('f', file.read(4))[0]
                function_object.left_min_value = struct.unpack('f', file.read(4))[0]
                function_object.left_max_value = struct.unpack('f', file.read(4))[0]
                
                #jump to tsgt_offset + 76 bytes
                file.seek(function_object.tsgt_offset + 0x4C)
                
                #grab Right values
                function_object.right_function_option = int.from_bytes(file.read(1), 'little')
                
                #jump to tsgt_offset + 80 bytes
                file.seek(function_object.tsgt_offset + 0x54)
                
                #grab right values
                function_object.right_frequency_value = struct.unpack('f', file.read(4))[0]
                function_object.right_phase_value = struct.unpack('f', file.read(4))[0]
                function_object.right_min_value = struct.unpack('f', file.read(4))[0]
                function_object.right_max_value = struct.unpack('f', file.read(4))[0]
         
                #repeat again for copy of all values?
                
            elif(function_object.option == 9): #option = exponent
                #jump to tsgt_offset + 56 bytes
                file.seek(function_object.tsgt_offset + 0x38)
                
                #grab left values
                function_object.left_min_value = struct.unpack('f', file.read(4))[0]
                function_object.left_max_value = struct.unpack('f', file.read(4))[0]
                function_object.left_exponent_value = struct.unpack('f', file.read(4))[0]
                
                #grab right values
                function_object.right_min_value = struct.unpack('f', file.read(4))[0]
                function_object.right_max_value = struct.unpack('f', file.read(4))[0]
                function_object.right_exponent_value = struct.unpack('f', file.read(4))[0]
                
                #repeat again for copy of all values?
                
            elif(function_object.option == 2): #option = transition
                
                #jump to tsgt_offset + 56 bytes
                file.seek(function_object.tsgt_offset + 0x38) 
            
                #store left function option
                function_object.left_function_option = int.from_bytes(file.read(1), 'little')

                #jump to tsgt_offset + 60 bytes
                file.seek(function_object.tsgt_offset + 0x3C)
                
                #grab left values
                function_object.left_min_value = struct.unpack('f', file.read(4))[0]
                function_object.left_max_value = struct.unpack('f', file.read(4))[0]
                
                #jump to tsgt_offset + 68 bytes
                file.seek(function_object.tsgt_offset + 0x44)
                
                #grab Right values
                function_object.right_function_option = int.from_bytes(file.read(1), 'little')
                
                #jump to tsgt_offset + 72 bytes
                file.seek(function_object.tsgt_offset + 0x48)
                
                #grab right values
                function_object.right_min_value = struct.unpack('f', file.read(4))[0]
                function_object.right_max_value = struct.unpack('f', file.read(4))[0]
         
                #repeat again for copy of all values?
                
            else:
                print("Function Option issue")
            
        return function_object






    def print_function(function_object):
        print("----Function----")
        print("  Name: " + function_object.function_name)
        print("  Type: " + get_function_option(function_object.option))
        if(function_object.range_toggle == True):
            print("  Range Toggle: On")
            print("  Range Name: " + function_object.range_name)
        else:
            print("  Range Toggle: Off")
        print("  Time Period: " + str(function_object.time_period) + " seconds")
        print("  Main Min: " + str(function_object.main_min_value))    
        print("  Main Max: " + str(function_object.main_max_value))
        
        if(function_object.option == 3): #option = periodic
            print("  Left Function Option: " + get_periodic_option(function_object.left_function_option))
            print("  Left Frequency: " + str(function_object.left_frequency_value))
            print("  Left Phase: " + str(function_object.left_phase_value))    
            print("  Left Min: " + str(function_object.left_min_value))
            print("  Left Max: " + str(function_object.left_max_value))
            
            if(function_object.range_toggle == True):
                print("  Right Function Option: " + get_periodic_option(function_object.right_function_option))
                print("  Right Frequency: " + str(function_object.right_frequency_value))
                print("  Right Phase: " + str(function_object.right_phase_value))    
                print("  Right Min: " + str(function_object.right_min_value))
                print("  Right Max: " + str(function_object.right_max_value))
        
        if(function_object.option == 9): #option = exponent  
            print("  Left Min: " + str(function_object.left_min_value))
            print("  Left Max: " + str(function_object.left_max_value))
            print("  Left Exponent: " + str(function_object.left_exponent_value))
        
            if(function_object.range_toggle == True):   
                print("  Right Min: " + str(function_object.right_min_value))
                print("  Right Max: " + str(function_object.right_max_value))
                print("  Right Max: " + str(function_object.right_exponent_value))
        
        if(function_object.option == 2): #option = transition
            print("  Left Function Option: " + get_periodic_option(function_object.left_function_option))  
            print("  Left Min: " + str(function_object.left_min_value))
            print("  Left Max: " + str(function_object.left_max_value))
        
            if(function_object.range_toggle == True):
                print("  Right Function Option: " + get_periodic_option(function_object.right_function_option))   
                print("  Right Min: " + str(function_object.right_min_value))
                print("  Right Max: " + str(function_object.right_max_value))
    
    def get_bitmap_resolution(directory, choice):
        width = 0
        height = 0
        
        #open bitmap file in raw binary
        try:    
            bitmapfile = open(directory, "rb")
        except:
            curve_option = 6
            print("Resolution Error")
            return 6
       
        bitmap = bitmapfile.read()
        Res_Offset_Difference = 0x30
        Res_Offset = 0x0            
            
        #find pattern and save it to variable
        try: 
            Resolution_Offset = bitmap.index(b'\x00\x00\x00\x00\x61\x64\x67\x74\x00\x00\x00\x00\x00\x00\x00\x00\x6C\x62\x67\x74')
        except ValueError:
            print("Bitmap Curve Options not found!")

        if (Resolution_Offset != 0):
            Res_Offset = Resolution_Offset - Res_Offset_Difference
            
            bitmapfile.seek(Res_Offset)
            
            width = int.from_bytes(bitmapfile.read(2), 'little')
            height = int.from_bytes(bitmapfile.read(2), 'little')
            
            #print("curve_option: " + str(curve_option))
            bitmapfile.close()
            
            print("Texture Width: " + str(width))
            print("Texture Height: " + str(height))
        else:
            print("Resolution Offset Not Found!")
            
        if (choice == "width"):
            return width
        elif (choice == "height"):
            return height
        else: 
            "Error setting Resolution"
            return 0  
        
    def get_bitmap_curve (directory):
        curve_option = 0 
        
        #open bitmap file in raw binary
        try:    
            bitmapfile = open(directory, "rb")
        except:
            curve_option = 6
            print("Curve: " + get_bitmap_curve_option(curve_option))
            return 6
        bitmap = bitmapfile.read()
        Curve_Offset_Difference = 0x1F
        Curve_Offset = 0x0


        #find pattern and save it to variable
        try: 
            CurveOptions_Offset = bitmap.index(b'\x00\x00\x00\x00\x61\x64\x67\x74\x00\x00\x00\x00\x00\x00\x00\x00\x6C\x62\x67\x74')
        except ValueError:
            print("Bitmap Curve Options not found!")

        if (CurveOptions_Offset != 0):
            Curve_Offset = CurveOptions_Offset - Curve_Offset_Difference
            
            bitmapfile.seek(Curve_Offset)
            
            curve_option = int.from_bytes(bitmapfile.read(1), 'little')
            
            #print("curve_option: " + str(curve_option))
            bitmapfile.close()
            
            print("Curve: " + get_bitmap_curve_option(curve_option))
        else:
            print("Curve Options Pre Offset Not Found!")
        return curve_option

    def shift_mirror_wrap(Mirror_Group):
        Mirror_Group.inputs.get("Location").default_value = [0, 3, 0]
        
        return Mirror_Group

    def test_find(offset, shaderfile, type):
        type_byte_pattern = bytes(type, 'utf-8')
        shaderfile = open(ShaderPath, "rb")
        shaderfile_read = shaderfile.read()
        
        offset2 = shaderfile_read.find(type_byte_pattern, offset + len(type))
        #print("offset 1: " + str(offset))
        #print("offset 2: " + str(offset2))
        return offset2
        
        
    def make_gamma(node_tree, teximage_node, texture_type, gamma_value):
        if(texture_type == "base_map"):
            #create Gamma Node
            GammaNode_Base = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
            GammaNode_Base.inputs.get("Gamma").default_value = gamma_value

            #link Gamma Node
            pymat_copy.node_tree.links.new(GammaNode_Base.inputs["Color"], teximage_node.outputs["Color"])
        
        elif(texture_type == "detail_map"):
            #create Gamma Node
            GammaNode_Detail = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
            GammaNode_Detail.inputs.get("Gamma").default_value = gamma_value

            #link Gamma Node
            pymat_copy.node_tree.links.new(GammaNode_Detail.inputs["Color"], teximage_node.outputs["Color"])
        
        elif(texture_type == "bump_map"):
            #create Gamma Node
            GammaNode_Bump = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
            GammaNode_Bump.inputs.get("Gamma").default_value = gamma_value

            #link Gamma Node
            pymat_copy.node_tree.links.new(GammaNode_Bump.inputs["Color"], teximage_node.outputs["Color"])
        
        elif(texture_type == "bump_detail_map"):
            #create Gamma Node
            GammaNode_BumpDetail = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
            GammaNode_BumpDetail.inputs.get("Gamma").default_value = gamma_value

            #link Gamma Node
            pymat_copy.node_tree.links.new(GammaNode_BumpDetail.inputs["Color"], teximage_node.outputs["Color"])

        elif(texture_type == "self_illum_map"):
            #create Gamma Node
            GammaNode_SelfIllum = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
            GammaNode_SelfIllum.inputs.get("Gamma").default_value = gamma_value

            #link Gamma Node
            pymat_copy.node_tree.links.new(GammaNode_SelfIllum.inputs["Color"], teximage_node.outputs["Color"])

        elif(texture_type == "self_illum_detail_map"):
            #create Gamma Node
            GammaNode_SelfIllumDetail = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
            GammaNode_SelfIllumDetail.inputs.get("Gamma").default_value = gamma_value

            #link Gamma Node
            pymat_copy.node_tree.links.new(GammaNode_SelfIllumDetail.inputs["Color"], teximage_node.outputs["Color"])
        else:
            print("Unhandled texture type trying to be assinged a Gamma Node")
            
            
            
            
        # stop = 0
        # count = 0
        # offset = 0x0
        # offset_list = []
        # while stop != 1:
            # if (file.find(type_in_bytes, offset) != -1):
                # offset_list.append(file.find(type_byte_pattern, offset))
                # offset = offset_list[count] + len(type)
                
                # count = count + 1
            # else:
                # stop = 1
        # print("offset count: " + str(count))
        # print("offset list: " + offset_list)
        
        
        
        

    # def get_offset_list(file, ShaderItem, type)
        # type_byte_pattern = bytes(type, 'utf-8')
        # fileSizeBytes = os.path.getsize(file)
        
        # s = ConstBitStream(filename=file)
        
        
    # def parse(register_name,byte_data):
        # fileSizeBytes = os.path.getsize(file)
        # fileSizeMegaBytes = GetFileSize(os.path.getsize(bin_file))
        # data = open(bin_file, 'rb')

        # s = ConstBitStream(filename=bin_file)
        # occurances = s.findall(byte_data, bytealigned=True)
        # occurances = list(occurances)
        # totalOccurances = len(occurances)
        # byteOffset = 0                                                      # True start of Byte string 

        # for pymat_copy in range(0, len(occurances)):
            # occuranceOffset = (hex(int(occurances[pymat_copy]/8)))
            # s0f0, length, bitdepth, height, width = s.readlist('hex:16, uint:16, uint:8, 2*uint:16')  
            # s.bitpos = occurances[pymat_copy]
            # data = s.read('hex:32')      
            # print('Address: ' + str(occuranceOffset) + ' Data: ' + str(data))
            # csvWriter.writerow([register_name, str(occuranceOffset), str(data)])

        
    #DEPRECATED FOR ANOTHER TIME IF NEEDED
    # def has_scale(file, offset, directory_len):
        # scale_check_offset = 0x14
        # scale_check = 0

        # #seek to end of dir
        # dir_offset = file.seek(offset + directory_len) 
        
        # file.seek(file.tell() + scale_check_offset)
        
        # scale_check = int.from_bytes(file.read(1),'little')
        
        # if (scale_check == 2 or scale_check == 3 or scale_check == 4):
            # return True
        # else:
            # return False

    # def get_scale (file, offset, directory_len, scale_type): #scale type 0 = uniform  1 = X   2 = Y
        # scale_check_offset1 = 0x14 #check for 1st spot
        # scale_check_offset2 = 0x38 #check for 2nd spot
        # scale_check_offset3 = 0x5C #check for 3rd spot
        # scale_check1 = 1 
        # scale_check2 = 1
        # scale_check3 = 1
        
        # #seek to end of dir
        # dir_offset = file.seek(offset + directory_len)
        
        # #save temp value for scale check 1
        # file.seek(dir_offset + scale_check_offset1)
        # scale_check1 = int.from_bytes(file.read(1), 'little')
        # print("scale check1: " + str(scale_check1))
        
        # #save temp value for scale check 2
        # file.seek(dir_offset + scale_check_offset2)
        # scale_check2 = int.from_bytes(file.read(1), 'little')
        # print("scale check2: " + str(scale_check2))

        # #save temp value for scale check 3
        # file.seek(dir_offset + scale_check_offset3)
        # scale_check3 = int.from_bytes(file.read(1), 'little')
        # print("scale check3: " + str(scale_check3))    

        # #search for uniform value  when scale_type = 0
        # if(scale_type == 0):
            # if(scale_check1 == 2 or scale_check2 == 2 or scale_check3 == 2): #has uniform scale
                # if(scale_check1 == 2):
                    
                # elif(scale_check2 == 2):
                    
                # elif(scale_check3) == 2):
                    
            # else: #no uniform scaling data
                # return 1.00
        # #search for X value  when scale_type = 1

        
        # #search for Y value  when scale_type = 2


    def has_scale(file, offset, directory_len):
        tsgt = 1952936820 #tsgt in int values  
        no_scale_check_offset = 0x14 #saves 20 bytes ahead
        uniform_check_offset = 0x38 #saves 56 bytes ahead
        xy_scale_check_offset = 0x5C #saves 92 bytes ahead
        
        #seek to end of dir
        dir_offset = file.seek(offset + directory_len)  # + 0x2C) #seeks to offset which is at end of type and then 16 more bytes to get to start of directory for bitmap and skip number of bytes equal to characters in bitmap directory

        #save temp value for no_scale
        file.seek(dir_offset + no_scale_check_offset)
        no_scale_check = int.from_bytes(file.read(4), 'little')
        #print("no scale check: " + str(no_scale_check))
        
        #save temp value for uniform_scale
        file.seek(dir_offset + uniform_check_offset)
        uniform_scale_check = int.from_bytes(file.read(4), 'little')
        #print("uniform scale check: " + str(uniform_scale_check))
        
        #save temp value for xy_scale
        file.seek(dir_offset + xy_scale_check_offset)
        xy_scale_check = int.from_bytes(file.read(4), 'little')
        #print("xy scale check: " + str(xy_scale_check))
        
        #SEEK 20 bytes in from dir end
            #if it is 2 then it is uniform
            #if it is 3 then it is X
            #if it is 4 then it is Y
        
        #SEEK 56 bytes in from dir end
            #if it is 2 then it is uniform
            #if it is 3 then it is X
            #if it is 4 then it is Y
            
        #SEEK 92 bytes in from dir end
            #if it is 2 then it is uniform
            #if it is 3 then it is X
            #if it is 4 then it is Y
        
        if (no_scale_check == tsgt):
            #print("no scaling data returning 0")
            return 0
        elif (uniform_scale_check == tsgt):
            #print("Uniform Scale returning 1")
            return 1
        elif (xy_scale_check == tsgt):
            #print("XY Scale returning 2")
            return 2
        else: 
            #print("Scale data is fucked up bro")
            return 0

    #send in bitmap object with this to get all this data back
    def get_scale(file, offset, directory_len, bitmap_object):
        tsgt_byte_pattern = bytes("tsgt", 'utf-8')
        adgt_byte_pattern = bytes("adgt", 'utf-8')
        shaderfile = open(ShaderPath, "rb")
        shaderfile_read = shaderfile.read()
        tsgt_main_offset = 0x0
        tsgt_2_offset = 0x0
        isgt_1_offset = 0x0
        isgt_2_offset = 0x0
        adgt_offset = 0x0
        function_name_offset = 0x0
        range_name_offset = 0x0
        test_isgt = 0
        
        #clear data to be used in loops
        break_loop = 0
        test_bytes = 0
        transform_count = 0
        bitmap_object.transform_type_list = []
        bitmap_object.transform_value_list = []
        bitmap_object.function_list = [] #add on function object for each transform, even if empty
        function_object = function()
        function_object.tsgt_offset = 0x0
        function_object.option = 0
        function_object.range_toggle = False
        function_object.function_name = ""
        function_object.range_name = ""
        function_object.time_period = 0.00
        function_object.main_min_value = 0.00
        function_object.main_max_value = 0.00
        function_object.left_function_option = 0
        function_object.left_frequency_value = 0.00
        function_object.left_phase_value = 0.00
        function_object.left_min_value = 0.00
        function_object.left_max_value = 0.00
        function_object.left_exponent_value = 0.00
        function_object.right_function_option = 0
        function_object.right_frequency_value = 0.00
        function_object.right_phase_value = 0.00
        function_object.right_min_value = 0.00
        function_object.right_max_value = 0.00
        function_object.right_exponent_value = 0.00
        
        scaleuniform = 1.00
        scaleX = 1.00
        scaleY = 1.00
        transX = 0.00
        transY = 0.00
        
        
        
        #skip 20 bytes from dir end offset
        file.seek(offset + directory_len + 0x14)
        
        #loop to get all types of transforms present
        while (break_loop == 0):
            #save 4 bytes from current point to be tested
            test_bytes = int.from_bytes(file.read(4), 'little')
            
            #skip 32 bytes ahead
            file.seek(file.tell() + 0x20)
            
            if (test_bytes == 2):
                bitmap_object.transform_type_list.append("uniform")
                print("uniform scale found")
            elif (test_bytes == 3):
                bitmap_object.transform_type_list.append("scaleX")
                print("scale X found")
            elif (test_bytes == 4):
                bitmap_object.transform_type_list.append("scaleY")
                print("scale Y found")
            elif (test_bytes == 5):
                bitmap_object.transform_type_list.append("translateX")
                print("translation X found")
            elif (test_bytes == 6):
                bitmap_object.transform_type_list.append("translateY")
                print("translation Y found")
            else:
                #print("Error reaching transform type bytes")
                break_loop = 1
        #ends at beginning of 'tsgt'        
                
        #save size of array list as variable
        transform_count = len(bitmap_object.transform_type_list)     
        #print("transform count: " + str(transform_count))
        
        if(transform_count > 0):
            for j in range(transform_count):
            #clear function object
            #----FUNCTION BLOCK START---- basic and curve
            #check if next 4 bytes are tsgt
                #if not skip to offset of next tsgt
                test_tsgt = 0
                test_isgt = 0
                test_tsgt = int.from_bytes(file.read(4), 'little') #read 4 bytes ahead into into
                file.seek(file.tell() - 0x4) #go back 4
                #print("offset before: " + str(file.tell() - 36))
                if(test_tsgt != 1952936820): #if not equal to tsgt    
                    tsgt_main_offset = get_ASCII_offset(file, file.tell(), "tsgt") #jump to where tsgt starts in case there is a misalignment
                    #print("offset not at tsgt main")
                else:
                    tsgt_main_offset = file.tell() #save start of main 'tsgt'
                    #print("offset at tsgt main")
                    
                #print("tsgt main offset: " + str(tsgt_main_offset - 36))    
                function_name_offset = file.seek(tsgt_main_offset + 0x18) #skip 24 to right before Function Name
                
                #ADD FUNCTIONALITY FOR FUNCTION NAME AND RANGE NAME IF EVER NEEDED HERE
                
                
                # print("function name offset: " + str(function_name_offset - 36))
                # #test_isgt = int.from_bytes(file.read(4), 'little')  #test value to see if it is isgt  
                # #file.seek(file.tell() - 0x4)  
                # file.seek(function_name_offset)
                # print("current offset 2: " + str(file.tell() - 36))
                # print ("test isgt: " + str(test_isgt))
                # if (int.from_bytes(file.read(4), 'little') != 1952936809): #if isgt doesn't exist
                    # print("offset not at isgt 2. function name may be present")
                    # function_name_offset = file.tell()
                    # function_object.function_name = get_dir(file, file.tell()) #save function name
                    # isgt_2_offset = file.tell() + len(function_object.function_name) #skip to end of function name
                # else:
                    # isgt_2_offset = file.tell() #if isgt exists then save this location
                    # print("offset at isgt 2. no function name")
                
                # print("isgt 2 offset: " + str(isgt_2_offset - 36))
                # file.seek(isgt_2_offset + 0xC) #jump 12 bytes from isgt 2 offset to start of range name
                # test_tsgt = int.from_bytes(file.read(4), 'little')  #test value to see if it is isgt  
                # file.seek(file.tell() - 0x4)  
                # print("current offset 3: " + str(file.tell() - 36))
                # print ("test tsgt: " + str(test_tsgt))
                # if (test_tsgt != 1952936820): #if tsgt doesn't exists
                    # print("offset not at tsgt 2. range name may be present")
                    # range_name_offset = file.tell()
                    # function_object.range_name = get_dir(file, range_name_offset) #save function name
                    # function_object.range_name = (function_object.range_name)[:-1]
                    # tsgt_2_offset = file.tell() + len(function_object.range_name) #skip to end of function name
                # else:
                    # tsgt_2_offset = file.tell() #if isgt exists then save this location
                    # print("offset at tsgt 2. no range name ")
                    
                #print("tsgt 2 offset: " + str(tsgt_2_offset - 36))    
                
                #get the offset of 'adgt'
                adgt_offset = get_ASCII_offset(file, tsgt_main_offset, "adgt")
                #print("adgt offset: " + str(adgt_offset - 36))
                
                #seek from before 'adgt' + 12 bytes
                file.seek(adgt_offset + 0xC)
                
                #grab the function option
                function_object.option = int.from_bytes(file.read(1), 'little')
                
                #grab the range toggle
                function_object.range_toggle = int.from_bytes(file.read(1), 'little')
                
                #skip 2 bytes
                file.seek(file.tell() + 0x2)
                
                #grab main Min and main Max values
                function_object.main_min_value = struct.unpack('f', file.read(4))[0]
                #print("main min value 1: " + str(function_object.main_min_value))
                function_object.main_max_value = struct.unpack('f', file.read(4))[0]
                #print("main max value 1: " + str(function_object.main_max_value))
                
                #skip 20 bytes ahead to either end of block OR rest of data
                file.seek(file.tell() + 0x14)
                
                
                # 'tsgt'
                # 8 bytes
                # 'isgt'
                # 8 bytes
                # FUNCTION NAME GOES HERE
                
                # 'isgt'
                # 8 bytes
                
                # RANGE NAME GOES HERE
                
                # 'tsgt'
                # 8 bytes
                
                # 'adgt'
                # 8 bytes
                # type of function [1 byte int]
                # range toggle [1 byte int]
                # 2 bytes
                # Main Min value [4 byte float]
                # Main Max value [4 byte float]
                
                # 20 bytes
                #---Possible end or continuation of function--- exponent, periodic, transitional
                if(function_object.option == 3): #option = periodic    
                    print("periodic function")
                    #store left function option
                    function_object.left_function_option = int.from_bytes(file.read(1), 'little')

                    #jump 3 bytes
                    file.seek(file.tell() + 0x3)
                    
                    #grab left values
                    function_object.left_frequency_value = struct.unpack('f', file.read(4))[0]
                    function_object.left_phase_value = struct.unpack('f', file.read(4))[0]
                    function_object.left_min_value = struct.unpack('f', file.read(4))[0]
                    function_object.left_max_value = struct.unpack('f', file.read(4))[0]
                    
                    #grab Right values
                    function_object.right_function_option = int.from_bytes(file.read(1), 'little')
                    
                    #jump 3 bytes
                    file.seek(file.tell() + 0x3)
                    
                    #grab right values
                    function_object.right_frequency_value = struct.unpack('f', file.read(4))[0]
                    function_object.right_phase_value = struct.unpack('f', file.read(4))[0]
                    function_object.right_min_value = struct.unpack('f', file.read(4))[0]
                    function_object.right_max_value = struct.unpack('f', file.read(4))[0]
             
                    #repeat again for copy of all values?
                    bitmap_object.function_list.append(function_object)
                
                elif(function_object.option == 9): #option = exponent
                    print("exponent function")
                    #jump to start of values
                    
                    #grab left values
                    function_object.left_min_value = struct.unpack('f', file.read(4))[0]
                    function_object.left_max_value = struct.unpack('f', file.read(4))[0]
                    function_object.left_exponent_value = struct.unpack('f', file.read(4))[0]
                    
                    #grab right values
                    function_object.right_min_value = struct.unpack('f', file.read(4))[0]
                    function_object.right_max_value = struct.unpack('f', file.read(4))[0]
                    function_object.right_exponent_value = struct.unpack('f', file.read(4))[0]
                    
                    #repeat again for copy of all values?
                    bitmap_object.function_list.append(function_object)
                        
                elif(function_object.option == 2): #option = transition
                    print("transition function")
                    #jump to start of data if need be
                
                    #store left function option
                    function_object.left_function_option = int.from_bytes(file.read(1), 'little')

                    #jump 3 bytes
                    file.seek(file.tell() + 0x3)
                    
                    #grab left values
                    function_object.left_min_value = struct.unpack('f', file.read(4))[0]
                    function_object.left_max_value = struct.unpack('f', file.read(4))[0]
                    
                    #jump to data
                    
                    #grab Right values
                    function_object.right_function_option = int.from_bytes(file.read(1), 'little')
                    
                    #jump 3 bytes
                    file.seek(file.tell() + 0x3)
                    
                    #grab right values
                    function_object.right_min_value = struct.unpack('f', file.read(4))[0]
                    function_object.right_max_value = struct.unpack('f', file.read(4))[0]
             
                    #repeat again for copy of all values?
                    bitmap_object.function_list.append(function_object)
                else:
                    print("basic or curve function")
                    #if function option is either curve or basic then save function data
                    bitmap_object.function_list.append(function_object)
            
               # print("   min value " + str(j) + ": " + str(bitmap_object.function_list[j].main_min_value))
              #  print("   max value " + str(j) + ": " + str(bitmap_object.function_list[j].main_max_value))    
               # print("")
                
            
        #build bitmap_object with grabbed data abouts scaling and translation
       # for h in range(transform_count):
               # print(bitmap_object.transform_type_list[j])
               # print("main min value " + str(j) + ": " + str(bitmap_object.function_list[j].main_min_value))
                if (bitmap_object.transform_type_list[j] == "uniform"): #transform is uniform scale
                    print("setting uniform scale")
                    bitmap_object.scale_uniform = bitmap_object.function_list[j].main_min_value
                    if(bitmap_object.function_list[j].range_toggle == 25): #toggle is on
                        #half the value between max and min
                        print("Toggle found")
                elif (bitmap_object.transform_type_list[j] == "scaleX"): #transform is scale X
                    print("setting scale X")
                    scaleX = bitmap_object.function_list[j].main_min_value
                    if(bitmap_object.function_list[j].range_toggle == 25): #toggle is on
                        #half the value between max and min
                        print("Toggle found")
                elif (bitmap_object.transform_type_list[j] == "scaleY"): #transform is scale Y
                    print("setting scale Y")
                    scaleY = bitmap_object.function_list[j].main_min_value
                    if(bitmap_object.function_list[j].range_toggle == 25): #toggle is on
                        #half the value between max and min 
                        print("Toggle found")
                elif (bitmap_object.transform_type_list[j] == "translateX"): #transform is scale X
                    print("setting translation X")
                    transX = bitmap_object.function_list[j].main_min_value
                    if(bitmap_object.function_list[j].range_toggle == 25): #toggle is on
                        #half the value between max and min
                        print("Toggle found")
                elif (bitmap_object.transform_type_list[j] == "translateY"): #transform is scale X
                    print("setting translation Y")
                    transY = bitmap_object.function_list[j].main_min_value
                    if(bitmap_object.function_list[j].range_toggle == 25): #toggle is on
                        #half the value between max and min 
                        print("Toggle found")
                else: 
                    print("transform type error")
        
        
        print("scale uniform: " + str(bitmap_object.scale_uniform))
        print("scale X: " + str(scaleX))
        print("scale Y: " + str(scaleY))
        print("translate X: " + str(transX))
        print("translate Y: " + str(transY))
        
        if(scaleX != 1.0 and scaleY != 1.0):
            temp_list = []
            temp_list.append(scaleX)
            temp_list.append(scaleY)
            bitmap_object.scale_xy = temp_list
        if(transX != 0.0 and transY != 0.0):
            temp_trans_list = []
            temp_trans_list.append(transX)
            temp_trans_list.append(transY)
            bitmap_object.translation_xy = temp_trans_list
            
        return bitmap_object
           
    #checks if bitmap type has mirror mode on       
    def has_mirror_wrap(ShaderItem, bitmap_type):
        temp_val = 0
        index = 0
        max = len(ShaderItem.wrap_mode_list)
        
        print("checking for mirror for: " + bitmap_type)
        while (temp_val != 1):
            if(ShaderItem.wrap_mode_list[index].bitmap_type == bitmap_type or index == (max - 1)):
                temp_val = 1
            else:
                index = index + 1
        
        if (ShaderItem.wrap_mode_list[index].option == 2):
            print("    match!")
            return True
            
        else:
            return False
        
        # if (bitmap_type in ShaderItem.wrap_mode_list):
            # if(
        
        # for bitmap in range(len(ShaderItem.wrap_mode_list)):
            # #if bitmap types match
            # #print("1: " + ShaderItem.wrap_mode_list[bitmap].bitmap_type + "test")
            # #print("2: " + bitmap_type + "test")
            # if(ShaderItem.wrap_mode_list[bitmap].bitmap_type == bitmap_type):
                # #if wrap mode for that bitmap type is set to mirror
                # if (ShaderItem.wrap_mode_list[bitmap].option == 2):
                    # print("Mirror mapping found for " + bitmap_type)
                    # return True
            
        # return False
        
        
       
    #get the wrap mode of certain textures
    def get_wrap_mode_list(file, shader_type, ShaderItem):
        wrap_mode_object = wrap_mode()
        num_recorded_bitmaps = len(ShaderItem.bitmap_list)
        
        shaders_count = 0
        mtib_count = 0
        curr_offset = 0x0
        true_bitmap_count = 0
        temp_wrap_list = []
        temp_type_list = []
        last_mtib_offset = 0x0
        type_offset = 0x0
        after_type_offset = 0x0
        
        #print("get_wrap function")
        if(shader_type == 0):    
            file_read = file.read()
            
            try:
                #search for the first offset of fdmrshaders\shader
                #shader_shader_offset = file_read.index(b'\x66\x64\x6D\x72\x73\x68\x61\x64\x65\x72\x73\x5C\x73\x68\x61\x64\x65\x72\x6C\x62\x67\x74')
                shader_shader_offset = test_find(curr_offset, file, "fdmrshaders\shader")
                #print("fdmrshaders\shader_offset: " + str(shader_shader_offset))
            except ValueError:
                print("fmdrshaders\shader not found")
            
            #if the offset exists
            if(shader_shader_offset != 0):
                #loop through all counts of fdmrshaders\shader
                while(test_find(curr_offset, file, "fdmrshaders\shader") != -1):
                    curr_offset = test_find(curr_offset, file, "fdmrshaders\shader") #save next offset if value is found
                    shaders_count = shaders_count + 1
                    
                #reset curr_offset
                curr_offset = 0x0

                #loop through all counts of mtib            
                while(test_find(curr_offset, file, "mtib") != -1):
                    curr_offset = test_find(curr_offset, file, "mtib") #save next offset if value is found
                    mtib_count = mtib_count + 1
                    #print("mitb curr_dir offset: " + str(curr_offset))
                
                #print("mtib: " + str(mtib_count))
                if(shaders_count == 1):
                    true_bitmap_count = int(mtib_count / 2)
                elif(shaders_count == 2):
                    true_bitmap_count = int(mtib_count / 4)
                else:
                    print("something has gone wrong with get_wrap_mode_list function")
                
                #print("True bitmap count: " + str(true_bitmap_count))
                #loop a search for each mtib
                    #skip 30 bytes after start of each mtib to get option for wrap
                #print("shader shader: " + str(shader_shader_offset))
                #seek to shaders/shaderlbgt
                file.seek(shader_shader_offset)
                        
                #grab list of wrap options        
                for mtib1 in range(true_bitmap_count):
                    file.seek(test_find(file.tell(), file, "mtib")) #jump to nearest mtib
                    #print("before 30 bytes: " + str(file.tell()))
                    file.seek(file.tell() + 0x18) #skip 24 bytes
                    #print("mitb curr_dir offset: " + str(file.tell()))
                    temp_wrap_list.append(int.from_bytes(file.read(2), 'little')) #store 2 byte value in temp list
                    
                    
                    #print("option: " + str(temp_wrap_list[mtib1]))
                    last_mtib_offset = file.tell() #store this location for later
                    file.seek(last_mtib_offset)
                
            
                #grab the list of bitmap types
                for mtib2 in range(true_bitmap_count):
                    curr_offset = file.seek(test_find(file.tell(), file, "mtib"))
                    file.seek(curr_offset)
                    after_type_offset = file.tell() - 0xC #go back 12 bytes to end of type name
                    #print("After type offset: " + str(after_type_offset))
                    type_offset = get_before_type_offset(file, after_type_offset)
                    temp_type_list.append(get_ascii_string(file, type_offset, after_type_offset - type_offset).strip())
                    file.seek(curr_offset + 0x4)
        
            #join together temp_type_list and temp_wrap_list and store within wrap_mode_object
            #iterate through bitmap list that are stored
            for bitmaps in range(num_recorded_bitmaps):
                #iterate through true bitmap list to find matches
                for j in range(true_bitmap_count):
                    #if match is found
                    if(ShaderItem.bitmap_list[bitmaps].type == temp_type_list[j]):
                        #check if option == 2 and if it is then mark it in the bitmap object
                        ShaderItem.bitmap_list[bitmaps].wrap_option = temp_wrap_list[j]
                    
                    
                    
                    #wrap_mode_object.bitmap_type = temp_type_list[j]
                
                    #print(temp_type_list[j])
                    #print("option: " + str(temp_wrap_list[j]))
                
                    #wrap_mode_list.append(wrap_mode_object)
        
        return ShaderItem


    def get_scale_uniform(file, offset, directory_len):    
        file.seek(offset + directory_len + 0x78) #skips 120 bytes after dir to where the scaling data is at
        value = struct.unpack('f', file.read(4))[0]
        
        print("Uniform Scale: " + str(value))
        return value
        
    def get_scale_xy(file, offset, directory_len):
        X_Scale = 1.00
        Y_Scale = 1.00
        Temp_List = []
        
        file.seek(offset + directory_len + 0x9C) #skips 156 bytes from dir to get X scale
        X_Scale = struct.unpack('f', file.read(4))[0]
        
        file.seek(offset + directory_len + 0xF8) #skips 248 bytes from dir to get Y scale
        Y_Scale = struct.unpack('f', file.read(4))[0]
        
        Temp_List.append(X_Scale)
        Temp_List.append(Y_Scale)
        
        print("XY Scale: " + str(Temp_List))
        
        return Temp_List

    def has_rgb_alpha(file, offset):
        file.seek(offset + 0x84 - 0x4) #skips 132 bytes then back 4
        test_bytes = 0
        test_bytes = int.from_bytes(file.read(4), 'little') #checks for isgt
        if (test_bytes == 1952936809):
            return True #has both!
        else:
            return False

    def has_rgb(file, offset):
        file.seek(offset + 0x84)
        test_float = 0.00
        test_float = struct.unpack('f', file.read(4))[0]
        #print("test float: " + str(test_float))
        #if (test_float < 0.00 or test_float > 1000): #if float value is too big or too small
        test_float_str = str(test_float)
        if 'e' in test_float_str.lower():
            #print("Bad Float detected for value. It is color!")
            return True
        else:
            #print("Good float detected for value. It is value!")
            return False

    def get_rgb(file, offset, value):
        temp_rgb_list = []
        temp_alpha = 1.00
        
        #print("rgb 0")
        if (value == "rgb"):
            #print("rgb 1")
            
            #rgb or alpha can be at either 0xA8 or 0x104
            if(has_rgb_alpha(file, offset) == True): #has both
                #print("rgb2")
                file.seek(offset + 0xA8) #save first value as float to test
                test_float = struct.unpack('f', file.read(4))[0] #save as float
                test_float_str = str(test_float) #turn float into string
                if 'e' in test_float_str.lower(): #if float has e in it then not rgb value
                    file.seek(offset + 0xA8) #skips 168 bytes to where the color data is at

                    A = 1.00
                    B = float(int.from_bytes(file.read(1), 'little')) / 255
                    G = float(int.from_bytes(file.read(1), 'little')) / 255
                    R = float(int.from_bytes(file.read(1), 'little')) / 255
                    
                    temp_rgb_list.append(R)    
                    temp_rgb_list.append(G) 
                    temp_rgb_list.append(B)
                    temp_rgb_list.append(A)
                else:
                    file.seek(offset + 0x104) #skips 260 bytes to where the color data is at

                    A = 1.00
                    B = float(int.from_bytes(file.read(1), 'little')) / 255
                    G = float(int.from_bytes(file.read(1), 'little')) / 255
                    R = float(int.from_bytes(file.read(1), 'little')) / 255
                    
                    temp_rgb_list.append(R)    
                    temp_rgb_list.append(G) 
                    temp_rgb_list.append(B)
                    temp_rgb_list.append(A)   
                if (math.isnan(test_float)): #if FFFF then make default  
                    temp_rgb_list = color_white_rgb
            elif(has_rgb(file, offset) == True): #only rgb
                #print("rgb3")
                file.seek(offset + 0x84) #skips 132 bytes to where the color data is at

                A = 1.00
                B = float(int.from_bytes(file.read(1), 'little')) / 255
                G = float(int.from_bytes(file.read(1), 'little')) / 255
                R = float(int.from_bytes(file.read(1), 'little')) / 255
                
                
                #print("rgb test: " + str(temp_rgb_list))
                temp_rgb_list.append(R)    
                temp_rgb_list.append(G) 
                temp_rgb_list.append(B)
                temp_rgb_list.append(A)
                #print("rgb test: " + str(temp_rgb_list))
            else: #only alpha   
                #print("rgb4")
                temp_rgb_list.append(1.00)
                temp_rgb_list.append(1.00)
                temp_rgb_list.append(1.00)
                temp_rgb_list.append(1.00)

            #print("RGB Value: " + str(temp_rgb_list))
            return temp_rgb_list
            
        elif (value == "alpha"): #if value == alpha
            #print("rgb5")
            if(has_rgb_alpha(file, offset) == True): #has both
                #print("rgb6")
                file.seek(offset + 0xA8) #save first value as float to test
                test_float = struct.unpack('f', file.read(4))[0] #save as float
                test_float_str = str(test_float) #turn float into string
                if 'e' in test_float_str.lower(): #if float has e in it then not rgb value
                
                    file.seek(offset + 0x104) #skips 268 bytes to where the alpha data is at

                    temp_alpha = struct.unpack('f', file.read(4))[0]
                    
                    if (math.isnan(temp_alpha)): #if FFFF then make default
                        temp_alpha = 1.00
                else:
                    file.seek(offset + 0xA8) #skips 168 bytes to where the alpha data is at

                    temp_alpha = struct.unpack('f', file.read(4))[0]  

                    if (math.isnan(temp_alpha)): #if FFFF then make default
                        temp_alpha = 1.00                
            elif(has_rgb(file, offset) == True): #only rgb
                #print("rgb7")
                temp_alpha = 1.00
            else: #only alpha   
                #print("rgb8")
                
                file.seek(offset + 0x84) #skips 132 bytes to where the color data is at

                temp_alpha = struct.unpack('f', file.read(4))[0]
                
                if (math.isnan(temp_alpha)): #if FFFF then make default
                    temp_alpha = 1.00
                
            return temp_alpha
       
        
    def get_value(file, offset):
        file.seek(offset + 0x84) #skips to 132 bytes to where values live
        value = struct.unpack('f', file.read(4))[0]
        #print("Value: " + str(value))
        return value
        
        
        
    #Checks if a directory is valid or not
    def is_valid_dir(directory):
        if (directory.split('/')[0] == 'ai' or directory.split('/')[0] == 'camera' or directory.split('/')[0] == 'cinematics' or directory.split('/')[0] == 'effects' or directory.split('/')[0] == 'fx' or directory.split('/')[0] == 'globals' or directory.split('/')[0] == 'levels' or directory.split('/')[0] == 'multiplayer' or directory.split('/')[0] == 'objects' or directory.split('/')[0] == 'rasterizer' or directory.split('/')[0] == 'shaders' or directory.split('/')[0] == 'sound' or directory.split('/')[0] == 'ui'):
            return True
        else:
            return False
        
    def get_albedo_foliage_option(option):  
        if (option == 0):
            return "default"
        else:
            return "error reading value"

    def get_alpha_foliage_option(option):  
        if (option == 0):
            return "none"
        elif (option == 1):
            return "simple"
        else:
            return "error reading value"

    def get_material_foliage_option(option):  
        if (option == 0):
            return "default"
        else:
            return "error reading value"

    def get_color_option(option):  
        if (option == 2):
            return "2-color"
        elif (option == 3):
            return "3-color"
        elif (option == 4):
            return "4-color"
        else:
            return "error reading color option value"


    def get_albedo_option(option):
        if (option == 0):
            return "default"
        elif (option == 1):
            return "detail_blend"
        elif (option == 2):
            return "constant_color"
        elif (option == 3):
            return "two_change_color"
        elif (option == 4):
            return "four_change_color"
        elif (option == 5):
            return "three_detail_blend"
        elif (option == 6):
            return "two_detail_overlay"
        elif (option == 7):
            return "two_detail"
        elif (option == 8):
            return "color_mask"
        elif (option == 9):
            return "two_detail_black_point"
        elif (option == 10):
            return "two_change_color_anim_overlay"
        elif (option == 11):
            return "chameleon"
        elif (option == 12):
            return "two_change_color_chameleon"
        elif (option == 13):
            return "chameleon_masked"   
        elif (option == 14):
            return "color_mask_hard_light"   
        elif (option == 15):
            return "two_change_color_tex_overlay"   
        elif (option == 16):
            return "chameleon_albedo_masked"   
        elif (option == 17):
            return "custom_cube"   
        elif (option == 18):
            return "two_color"           
        elif (option == 19):
            return "scrolling_cube_mask"   
        elif (option == 20):
            return "scrolling_cube"   
        elif (option == 21):
            return "scrolling_texture_uv"   
        elif (option == 22):
            return "texture_from_misc"   
        else:
            return "ERROR"
            
    def get_bump_mapping_option(option):
        if (option == 0):
            return "off"
        elif (option == 1):
            return "standard"
        elif (option == 2):
            return "detail"   
        elif (option == 3):
            return "detail_masked"
        elif (option == 4):
            return "detail_plus_detail_masked"
        elif (option == 5):
            return "detail_unorm"
        else:
            return "ERROR"
            
    def get_alpha_test_option(option):
        if (option == 0):
            return "none"
        elif (option == 1):
            return "simple"
        else:
            return "ERROR"
            
    def get_specular_mask_option(option):        
        if (option == 0):
            return "no_specular_mask"
        elif (option == 1):
            return "specular_mask_from_diffuse"
        elif (option == 2):
            return "specular_mask_from_texture"
        elif (option == 3):
            return "specular_mask_from_color_texture"
        else:
            return "ERROR"
            
    def get_material_model_option(option):
        if (option == 0):
            return "diffuse_only"    
        elif (option == 1):
            return "cook_torrance"
        elif (option == 2):
            return "two_lobe_phong"
        elif (option == 3):
            return "foliage"
        elif (option == 4):
            return "none"
        elif (option == 5):
            return "glass"
        elif (option == 6):
            return "organism"
        elif (option == 7):
            return "single_lobe_phong"        
        elif (option == 8):
            return "car_paint"
        elif (option == 9):
            return "cook_torrance_custom_cube"
        elif (option == 10):
            return "cook_torrance_pbr_maps"
        elif (option == 11):
            return "cook_torrance_rim_fresnel"
        elif (option == 12):
            return "cook_torrance_scrolling_cube"        
        elif (option == 13):
            return "cook_torrance_from_albedo"   
        else:
            return "ERROR"
            
    def get_environment_map_option(option):
        if (option == 0):
            return "none"
        elif (option == 1):
            return "per_pixel"   
        elif (option == 2):
            return "dynamic"     
        elif (option == 3):
            return "from_flat_texture"     
        elif (option == 4):
            return "custom_map"     
        elif (option == 5):
            return "from_flat_exture_as_cubemap"     
        else:
            return "ERROR"
            
    def get_self_illumination_option(option):
        if (option == 0):
            return "off"
        elif (option == 1):
            return "simple" 
        elif (option == 2):
            return "3_channel_self_illum" 
        elif (option == 3):
            return "plasma" 
        elif (option == 4):
            return "from_diffuse" 
        elif (option == 5):
            return "illum_detail" 
        elif (option == 6):
            return "meter" 
        elif (option == 7):
            return "self_illum_times_diffuse" 
        elif (option == 8):
            return "simple_with_alpha_mask" 
        elif (option == 9):
            return "simple_four_change_color"         
        elif (option == 10):
            return "illum_detail_world_space_four_cc"     
        elif (option == 11):
            return "illum_change_color" 
        else:
            return "ERROR"
            
    #get halogram options
    def get_halogram_self_illumination_option(option):
        if (option == 0):
            return "off"
        elif (option == 1):
            return "simple" 
        elif (option == 2):
            return "3_channel_self_illum" 
        elif (option == 3):
            return "plasma" 
        elif (option == 4):
            return "from_diffuse" 
        elif (option == 5):
            return "illum_detail" 
        elif (option == 6):
            return "meter" 
        elif (option == 7):
            return "self_illum_times_diffuse" 
        elif (option == 8):
            return "multilayer_additive" 
        elif (option == 9):
            return "scope_blur"         
        elif (option == 10):
            return "ml_add_four_change_color"     
        elif (option == 11):
            return "ml_add_five_change_color" 
        elif (option == 12):
            return "plasma_wide_and_sharp_five_change_color"     
        elif (option == 13):
            return "self_illum_holograms" 
        else:
            return "ERROR"     
            
    def get_blend_mode_option(option):
        if (option == 0):
            return "opaque"
        elif (option == 1):
            return "additive"             
        elif (option == 2):
            return "multiply"             
        elif (option == 3):
            return "alpha_blend"             
        elif (option == 4):
            return "double_multiply"             
        elif (option == 5):
            return "pre_multiplied_alpha"             
        else:
            return "ERROR"
            
    def get_parallax_option(option):
        if(option == 0):
            return "off"
        elif (option == 1):
            return "simple"             
        elif (option == 2):
            return "interpolated"             
        elif (option == 3):
            return "simple_detail" 
        else:
            return "ERROR"
            
    def get_misc_option(option):
        if(option == 0):
            return "first_person_never"
        elif (option == 1):
            return "first_person_sometimes" 
        elif (option == 2):
            return "first_person_always"    
        elif (option == 3):
            return "first_person_never_w/rotating_bitmaps"             
        else:
            return "ERROR"

    def get_bitmap_curve_option(option):
        if (option == 0):
            return "unknown"   #has gamma SOMETIMES, mostly not tho
        elif (option == 1):
            return "xRGB"      #has gamma
        elif (option == 2):
            return "gamma 2.0" #has gamma
        elif (option == 3):
            return "linear"
        elif (option == 4):
            return "offset log"
        elif (option == 5):
            return "sRGB"
        elif (option == 6):
            return "Default Data"
        else:
            return "ERROR"
            
    def get_function_option(option):
        if(option == 1):
            return "basic"
        elif(option == 8):
            return "curve"
        elif(option == 3):
            return "periodic"
        elif(option == 9):
            return "exponent"
        elif(option == 2):
            return "transition"
        else:
            return "Error getting function option"
            
    def get_periodic_option(option):
        if(option == 0):
            return "one"
        elif(option == 1):
            return "zero"
        elif(option == 2):
            return "cosine"
        elif(option == 3):
            return "cosine [variable period]"
        elif(option == 4):
            return "diagonal wave"
        elif(option == 5):
            return "diagonal wave [variable period]"
        elif(option == 6):
            return "slide"
        elif(option == 7):
            return "slide [variable period]"
        elif(option == 8):
            return "noise"        
        elif(option == 9):
            return "jitter"
        elif(option == 10):
            return "wander"
        elif(option == 11):
            return "spark"
        else:
            return "Error getting periodic option"        

    def get_transition_option(option):
        if(option == 0):
            return "linear"
        elif(option == 1):
            return "early"
        elif(option == 2):
            return "very early"
        elif(option == 3):
            return "late"
        elif(option == 4):
            return "very late"
        elif(option == 5):
            return "cosine"
        elif(option == 6):
            return "one"
        elif(option == 7):
            return "zero"
        else:
            return "Error getting transition option"


    def get_blending_option(option):
        if(option == 0):
            return "morph"
        elif(option == 1):
            return "dynamic morph"
        else:
            return "Error getting Blending Option"

    def get_environment_map_terr_option(option):
        if(option == 0):
            return "none"
        elif(option == 1):
            return "per_pixel"
        elif(option == 2):
            return "dynamic"    
        return "Error getting Environment Map Terr Option"

    def get_material_0_option(option):
        if(option == 0):
            return "diffuse_only"
        elif(option == 1):
            return "diffuse_plus_specular"
        elif(option == 2):
            return "off"
        elif(option == 3):
            return "diffuse_only_plus_self_illum"
        elif(option == 4):
            return "diffuse_plus_specular_plus_self_illum"
        elif(option == 5):
            return "diffuse_plus_specular_plus_heightmap"
        elif(option == 6):
            return "diffuse_plus_two_detail"
        elif(option == 7):
            return "diffuse_plus_specular_plus_up_vector_plus_heightmap"
        else:
            return "Error getting Material_0 option"

    def get_material_1_option(option):
        if(option == 0):
            return "diffuse_only"
        elif(option == 1):
            return "diffuse_plus_specular"
        elif(option == 2):
            return "off"
        elif(option == 3):
            return "diffuse_only_plus_self_illum"
        elif(option == 4):
            return "diffuse_plus_specular_plus_self_illum"
        elif(option == 5):
            return "diffuse_plus_specular_plus_heightmap"
        elif(option == 6):
            return "diffuse_plus_two_detail"
        elif(option == 7):
            return "diffuse_plus_specular_plus_up_vector_plus_heightmap"
        else:
            return "Error getting Material_1 option"

    def get_material_2_option(option):
        if(option == 0):
            return "diffuse_only"
        elif(option == 1):
            return "diffuse_plus_specular"
        elif(option == 2):
            return "off"
        elif(option == 3):
            return "diffuse_only_plus_self_illum"
        elif(option == 4):
            return "diffuse_plus_specular_plus_self_illum"
        else:
            return "Error getting Material_2 option"

    def get_material_3_option(option):
        if(option == 0):
            return "off"
        elif(option == 1):
            return "diffuse_only_(four_material_shaders_disable_detail_bump)"
        elif(option == 2):
            return "diffuse__plus_specular_(four_material_shaders_disable_detail_bump)"
        else:
            return "Error getting Material_3 option"


            
    def get_warp_option(option):
        if (option == 0):
            return "none"
        elif (option == 1):
            return "from_texture" 
        elif (option == 2):
            return "parallax_simple" 
        else:
            return "ERROR"        
            
    def get_overlay_option(option):
        if (option == 0):
            return "none"
        elif (option == 1):
            return "additive" 
        elif (option == 2):
            return "additive_detail" 
        elif (option == 3):
            return "multiply" 
        elif (option == 4):
            return "multiply_and_additive_detail" 
        else:
            return "ERROR"        
            
    def get_edge_fade_option(option):
        if (option == 0):
            return "none"
        elif (option == 1):
            return "simple" 
        else:
            return "ERROR"

    def get_distortion_option(option):
        if (option == 0):
            return "off"
        elif (option == 1):
            return "on" 
        else:
            return "ERROR"
      
    def get_soft_fade_option(option):
        if (option == 0):
            return "off"
        elif (option == 1):
            return "on" 
        else:
            return "ERROR"
      

    def uses_gray_50(type):
        if (type == "base_map"):
            return True
        elif (type == "change_color_map"):
            return True
        elif (type == "secondary_color_map"):
            return True
        elif (type == "base_masked_map"):
            return True
        elif (type == "custom_cube"):
            return True
        elif (type == "blend_map"):
            return True
        elif (type == "color_blend_mask_cubemap"):
            return True
        elif (type == "color_cubemap"):
            return True
        elif (type == "color_texture"):
            return True
        elif (type == "material_model"):
            return True
        elif (type == "material_texture"):
            return True
        elif (type == "custom_cube"):
            return True
        elif (type == "spec_tint_map"):
            return True
        elif (type == "spec_blend_map"):
            return True
        elif (type == "normal_specular_tint_map"):
            return True
        elif (type == "glancing_specular_tint_map"):
            return True
        elif (type == "tint_blend_mask_cubemap"):
            return True
        elif (type == "spec_tint_cubemap"):
            return True
        elif (type == "self_illum_map"):
            return True
        elif (type == "noise_map_a"):
            return True
        elif (type == "noise_map_b"):
            return True
        elif (type == "height_map"):
            return True
        elif (type == "height_scale_map"):
            return True
        elif (type == "base_map_m_0"):
            return True
        elif (type == "base_map_m_1"):
            return True
        elif (type == "base_map_m_2"):
            return True
        elif (type == "base_map_m_3"):
            return True
        else:
            return False
            
    def uses_default_detail(type):
        if (type == "detail_map"):
            return True
        elif (type == "detail_map2"):
            return True
        elif (type == "detail_map3"):
            return True
        elif (type == "detail_map_overlay"):
            return True
        elif (type == "self_illum_detail_map"):
            return True
        elif (type == "detail_map_m_0"):
            return True
        elif (type == "detail_map_m_1"):
            return True
        elif (type == "detail_map_m_2"):
            return True
        elif (type == "detail_map_m_3"):
            return True
        else:
            return False
            
    def uses_default_vector(type):
        if (type == "bump_map"):
            return True
        elif (type == "bump_detail_map"):
            return True
        elif (type == "bump_detail_masked_map"):
            return True
        elif (type == "distort_map"):
            return True
        elif (type == "bump_map_m_0"):
            return True
        elif (type == "bump_map_m_1"):
            return True
        elif (type == "bump_map_m_2"):
            return True
        elif (type == "bump_map_m_3"):
            return True        
        else:
            return False
            
    def uses_color_white(type):
        if (type == "chameleon_mask_map"):
            return True
        elif (type == "bump_map_mask_map"):
            return True
        elif (type == "specular_mask_map"):
            return True
        elif (type == "specular_map"):
            return True
        elif (type == "occlusion_parameter_map"):
            return True
        elif (type == "subsurface_map"):
            return True
        elif (type == "transparence_map"):
            return True
        else:
            return False
            
    def uses_reference_grids(type):
        if (type == "color_mask_map"):
            return True
        else:
            return False
            
    def uses_default_alpha_test(type):
        if (type == "alpha_test_map"):
            return True
        else:
            return False        

    def uses_default_dynamic_cube_map(type):
        if (type == "environment_map"):
            return True
        else:
            return False         
            
    def uses_color_red(type):
        if (type == "flat_environment_map"):
            return True
        else:
            return False          

    def uses_monochrome_alpha_grid(type):
        if (type == "meter_map"):
            return True
        else:
            return False         

    # def TextureNameEdit(ImageTexNode, BitmapType):
        # ImageTexNode.name = "[" + BitmapType + "]  " + ImageTexNode.name
        # return ImageTexNode


    def is_texture_needed(ShaderItem, texture_type):
        if texture_type in ShaderItem.needed_bitmaps:
            return True
        else:
            return False

    def correct_default_dir(bitmap_type):
        default_dir = ""
        
        if(uses_gray_50(bitmap_type) == True):
            default_dir = "shaders/default_bitmaps/bitmaps/gray_50_percent"
        elif(uses_color_white(bitmap_type) == True):
            default_dir = "shaders/default_bitmaps/bitmaps/color_white"
        elif(uses_default_vector(bitmap_type) == True):
            default_dir = "shaders/default_bitmaps/bitmaps/default_vector"
        elif(uses_reference_grids(bitmap_type) == True):    
            default_dir = "shaders/default_bitmaps/bitmaps/reference_grids"
        elif(uses_default_alpha_test(bitmap_type) == True):    
            default_dir = "shaders/default_bitmaps/bitmaps/default_alpha_test"
        elif(uses_default_dynamic_cube_map(bitmap_type) == True):    
            default_dir =  "shaders/default_bitmaps/bitmaps/default_dynamic_cube_map"
        elif(uses_color_red(bitmap_type) == True):    
            default_dir = "shaders/default_bitmaps/bitmaps/color_red"
        elif(uses_monochrome_alpha_grid(bitmap_type) == True):    
            default_dir = "shaders/default_bitmaps/bitmaps/monochrome_alpha_grid"
        else:
            default_dir = "shaders/default_bitmaps/bitmaps/default_detail"
        
        return default_dir

    #function to check if certain NodeGroup has what it needs for default textures
    def build_texture_list(ShaderItem, Shader_Type):
        #check needed bitmaps for the used categories
    
        ShaderItem.needed_bitmaps = []

        

##############
#.shader files
##############

        if(Shader_Type == 0):
        #albedo options
            if(ShaderItem.albedo_option == 0): #H3Category: albedo - default 
                ShaderItem.needed_bitmaps.append("base_map")
                ShaderItem.needed_bitmaps.append("detail_map")
            elif(ShaderItem.albedo_option == 1): #H3Category: albedo - detail_blend
                ShaderItem.needed_bitmaps.append("base_map")
                ShaderItem.needed_bitmaps.append("detail_map")
                ShaderItem.needed_bitmaps.append("detail_map2")
            elif(ShaderItem.albedo_option == 2): #H3Category: albedo - constant_color
                print("constant color doesn't need bitmaps")
            elif(ShaderItem.albedo_option == 3): #H3Category: albedo - two_change_color
                ShaderItem.needed_bitmaps.append("base_map")
                ShaderItem.needed_bitmaps.append("detail_map")
                ShaderItem.needed_bitmaps.append("change_color_map")
            elif(ShaderItem.albedo_option == 4): #H3Category: albedo - four_change_color
                ShaderItem.needed_bitmaps.append("base_map")
                ShaderItem.needed_bitmaps.append("detail_map")
                ShaderItem.needed_bitmaps.append("change_color_map")
            elif(ShaderItem.albedo_option == 5): #H3Category: albedo - three_detail_blend
                ShaderItem.needed_bitmaps.append("base_map")
                ShaderItem.needed_bitmaps.append("detail_map")
                ShaderItem.needed_bitmaps.append("detail_map2")
                ShaderItem.needed_bitmaps.append("detail_map3")
            elif(ShaderItem.albedo_option == 6): #H3Category: albedo - two_detail_overlay
                ShaderItem.needed_bitmaps.append("base_map")
                ShaderItem.needed_bitmaps.append("detail_map")
                ShaderItem.needed_bitmaps.append("detail_map2")
                ShaderItem.needed_bitmaps.append("detail_overlay")
            elif(ShaderItem.albedo_option == 7): #H3Category: albedo - two_detail
                ShaderItem.needed_bitmaps.append("base_map")
                ShaderItem.needed_bitmaps.append("detail_map")
                ShaderItem.needed_bitmaps.append("detail_map2")
            elif(ShaderItem.albedo_option == 8): #H3Category: albedo - color_mask    
                ShaderItem.needed_bitmaps.append("base_map")
                ShaderItem.needed_bitmaps.append("detail_map")
                ShaderItem.needed_bitmaps.append("color_mask")
            elif(ShaderItem.albedo_option == 9): #H3Category: albedo - two_detail_black_point    
                ShaderItem.needed_bitmaps.append("base_map")
                ShaderItem.needed_bitmaps.append("detail_map")
                ShaderItem.needed_bitmaps.append("detail_map2")
            elif(ShaderItem.albedo_option == 17): #H3Category: albedo - custom_cube
                ShaderItem.needed_bitmaps.append("base_map")
                ShaderItem.needed_bitmaps.append("custom_cube")
            elif(ShaderItem.albedo_option == 18): #H3Category: albedo - two_color
                ShaderItem.needed_bitmaps.append("base_map")
                ShaderItem.needed_bitmaps.append("blend_map")
            elif(ShaderItem.albedo_option == 21): #H3Category: albedo - scrolling_texture_uv
                ShaderItem.needed_bitmaps.append("base_map")
                ShaderItem.needed_bitmaps.append("color_texture")
            elif(ShaderItem.albedo_option == 22): #H3Category: albedo - texture_from_misc
                ShaderItem.needed_bitmaps.append("base_map")
                ShaderItem.needed_bitmaps.append("color_texture")
        #bump_map group
            if(ShaderItem.bump_mapping_option == 1): #H3Category: bump_mapping - standard
                ShaderItem.needed_bitmaps.append("bump_map")       
            if(ShaderItem.bump_mapping_option == 2): #H3Category: bump_mapping - detail
                ShaderItem.needed_bitmaps.append("bump_map")
                ShaderItem.needed_bitmaps.append("bump_detail_map")
            elif(ShaderItem.bump_mapping_option == 3): #H3Category: bump_mapping - detail_masked
                ShaderItem.needed_bitmaps.append("bump_map")
                ShaderItem.needed_bitmaps.append("bump_detail_map")
                ShaderItem.needed_bitmaps.append("bump_detail_mask_map")
            elif(ShaderItem.bump_mapping_option == 4): #H3Category: bump_mapping - detail_plus_detail_masked
                ShaderItem.needed_bitmaps.append("bump_map")
                ShaderItem.needed_bitmaps.append("bump_detail_map")
                ShaderItem.needed_bitmaps.append("bump_detail_mask_map")
                ShaderItem.needed_bitmaps.append("bump_detail_masked_map")
            #elif(ShaderItem.bump_mapping_option == 5): #H3Category: bump_mapping - detail_unorm
                #NodeGroup.inputs.get("bump_detail_coefficient").default_value = ShaderItem.bump_detail_coefficient            
            
        #environment map group    
            if(ShaderItem.environment_mapping_option == 1 or ShaderItem.environment_map_option == 1): #H3Category: environment_mapping - per_pixel
                ShaderItem.needed_bitmaps.append("environment_map")
            elif(ShaderItem.environment_mapping_option == 2 or ShaderItem.environment_map_option == 2): #H3Category: environment_mapping - dynamic
                print("dynamic env group needs no textures")
                
        #material model group        
            #if(ShaderItem.material_model_option == 0): #H3Category: mateiral_model - diffuse_only
                #no values needed
            if(ShaderItem.material_model_option == 6): #H3Category: material_model - organism
                ShaderItem.needed_bitmaps.append("specular_map")
                ShaderItem.needed_bitmaps.append("subsurface_map")
                ShaderItem.needed_bitmaps.append("transparence_map")
            #elif(ShaderItem.material_model_option == 2): #H3Category: material_model - two_lobe_phong
                          
            #elif(ShaderItem.material_model_option == 5): #H3Category: material_model - glass
                          
            #elif(ShaderItem.material_model_option == 7): #H3Category: material_model - single_lobe_phong
                
                    
        #self illum group
            if(ShaderItem.self_illumination_option == 1): #H3Category: self_illumination - simple
                ShaderItem.needed_bitmaps.append("self_illum_map")
            elif(ShaderItem.self_illumination_option == 2): #H3Category: self_illumination - 3_channel_self_illum
                ShaderItem.needed_bitmaps.append("self_illum_map")           
            elif(ShaderItem.self_illumination_option == 3): #H3Category: self_illumination - plasma
                ShaderItem.needed_bitmaps.append("noise_map_a")
                ShaderItem.needed_bitmaps.append("noise_map_b")
                ShaderItem.needed_bitmaps.append("alpha_mask_map")
            #elif(ShaderItem.self_illumination_option == 4): #H3Category: self_illumination - from_diffuse
                
            elif(ShaderItem.self_illumination_option == 5): #H3Category: self_illumination - illum_detail
                ShaderItem.needed_bitmaps.append("self_illum_map")
                ShaderItem.needed_bitmaps.append("self_illum_detail_map")
            elif(ShaderItem.self_illumination_option == 6): #H3Category: self_illumination - meter
                ShaderItem.needed_bitmaps.append("meter_map")
            elif(ShaderItem.self_illumination_option == 7): #H3Category: self_illumination - self_illum_times_diffuse
                ShaderItem.needed_bitmaps.append("self_illum_map")
            elif(ShaderItem.self_illumination_option == 8): #H3Category: self_illumination - simple_with_alpha_mask    
                ShaderItem.needed_bitmaps.append("self_illum_map")
               
        
            
        ##############    
        #terrain group
        ##############
        
        if(Shader_Type == 1):
            ShaderItem.needed_bitmaps.append("blend_map")
            
            ShaderItem.needed_bitmaps.append("base_map_m_0")
            ShaderItem.needed_bitmaps.append("detail_map_m_0")
            ShaderItem.needed_bitmaps.append("bump_map_m_0")
            ShaderItem.needed_bitmaps.append("detail_bump_m_0")
            
            ShaderItem.needed_bitmaps.append("base_map_m_1")
            ShaderItem.needed_bitmaps.append("detail_map_m_1")
            ShaderItem.needed_bitmaps.append("bump_map_m_1")
            ShaderItem.needed_bitmaps.append("detail_bump_m_1")
            
            ShaderItem.needed_bitmaps.append("base_map_m_2")
            ShaderItem.needed_bitmaps.append("detail_map_m_2")
            ShaderItem.needed_bitmaps.append("bump_map_m_2")
            ShaderItem.needed_bitmaps.append("detail_bump_m_2")

            ShaderItem.needed_bitmaps.append("base_map_m_3")
            ShaderItem.needed_bitmaps.append("detail_map_m_3")
            ShaderItem.needed_bitmaps.append("bump_map_m_3")
            ShaderItem.needed_bitmaps.append("detail_bump_m_3")

        #######################
        #.shader_halogram files
        #######################

        if(Shader_Type == 3):        
            if(ShaderItem.self_illumination_option == 8): #H3Category: self_illumination - multilayer_additive
                #add these in later
                print("self_illumination - multilayer_additive")
            elif(ShaderItem.self_illumination_option == 9): #H3Category: self_illumination - scope_blur
                #add these in later
                print("self_illumination - scope_blur")
            elif(ShaderItem.self_illumination_option == 10): #H3Category: self_illumination - ml_add_four_change_color
                #add these in later
                print("self_illumination - ml_add_four_change_color")
            elif(ShaderItem.self_illumination_option == 11): #H3Category: self_illumination - ml_add_five_change_color
                #add these in later
                print("self_illumination - ml_add_five_change_color")
            elif(ShaderItem.self_illumination_option == 12): #H3Category: self_illumination - plasma_wide_and_sharp_five_change_color
                #add these in later
                print("self_illumination - plasma_wide_and_sharp_five_change_color")
            elif(ShaderItem.self_illumination_option == 13): #H3Category: self_illumination - self_illum_holograms
                #add these in later
                print("self_illumination - self_illum_holograms")
        
        return ShaderItem


    #Apply values from ShaderItem to Shader 
    def apply_group_values(NodeGroup, ShaderItem, category):
        #albedo/base_map group
        if(category == "albedo"):
            if(ShaderItem.albedo_option == 0): #H3Category: albedo - default 
                NodeGroup.inputs.get("albedo_color").default_value = ShaderItem.albedo_color
                NodeGroup.inputs.get("albedo_color_alpha").default_value = ShaderItem.albedo_color_alpha
            #elif(ShaderItem.albedo_option == 1): #H3Category: albedo - detail_blend
                #no values needed?
            elif(ShaderItem.albedo_option == 2): #H3Category: albedo - constant_color
                NodeGroup.inputs.get("albedo_color").default_value = ShaderItem.albedo_color
                NodeGroup.inputs.get("albedo_color_alpha").default_value = ShaderItem.albedo_color_alpha
            #elif(ShaderItem.albedo_option == 3): #H3Category: albedo - two_change_color
                #no values needed?
            #elif(ShaderItem.albedo_option == 4): #H3Category: albedo - four_change_color
                #no values needed?
            #elif(ShaderItem.albedo_option == 5): #H3Category: albedo - three_detail_blend
                #no values needed?
            #elif(ShaderItem.albedo_option == 6): #H3Category: albedo - two_detail_overlay
                #no values needed?     
            #elif(ShaderItem.albedo_option == 7): #H3Category: albedo - two_detail
                #no values needed?
                
        #bump_map group
        elif(category == "bump"):
            #if(ShaderItem.bump_mapping_option == 1): #H3Category: bump_mapping - standard
                #no values needed?        
            if(ShaderItem.bump_mapping_option == 2): #H3Category: bump_mapping - detail
                NodeGroup.inputs.get("bump_detail_coefficient").default_value = ShaderItem.bump_detail_coefficient
            elif(ShaderItem.bump_mapping_option == 3): #H3Category: bump_mapping - detail_masked
                NodeGroup.inputs.get("albedo_color").default_value = ShaderItem.albedo_color
                #invert_mask?
            elif(ShaderItem.bump_mapping_option == 4): #H3Category: bump_mapping - detail_plus_detail_masked
                NodeGroup.inputs.get("bump_detail_coefficient").default_value = ShaderItem.bump_detail_coefficient
                #bump_detail_masked_coefficient  
            #elif(ShaderItem.bump_mapping_option == 5): #H3Category: bump_mapping - detail_unorm
                #NodeGroup.inputs.get("bump_detail_coefficient").default_value = ShaderItem.bump_detail_coefficient            
            
        #environment map group    
        elif(category == "env map"):
            if(ShaderItem.environment_mapping_option == 1 or ShaderItem.environment_map_option == 1): #H3Category: environment_mapping - per_pixel
                NodeGroup.inputs.get("env_tint_color").default_value = ShaderItem.env_tint_color
            elif(ShaderItem.environment_mapping_option == 2 or ShaderItem.environment_map_option == 2): #H3Category: environment_mapping - dynamic
                NodeGroup.inputs.get("env_tint_color").default_value = ShaderItem.env_tint_color        
                NodeGroup.inputs.get("env_roughness_scale").default_value = ShaderItem.env_roughness_scale  
                
        #material model group    
        elif(category == "mat model"):    
            #if(ShaderItem.material_model_option == 0): #H3Category: mateiral_model - diffuse_only
                #no values needed
            if(ShaderItem.material_model_option == 1): #H3Category: material_model - cook_torrance
                NodeGroup.inputs.get("diffuse_coefficient").default_value = ShaderItem.diffuse_coefficient
                NodeGroup.inputs.get("specular_coefficient").default_value = ShaderItem.specular_coefficient
                NodeGroup.inputs.get("specular_tint").default_value = ShaderItem.specular_tint
                NodeGroup.inputs.get("fresnel_color").default_value = ShaderItem.fresnel_color
                NodeGroup.inputs.get("roughness").default_value = ShaderItem.roughness
                NodeGroup.inputs.get("environment_map_specular_contribution").default_value = ShaderItem.environment_map_specular_contribution
                NodeGroup.inputs.get("use_material_texture").default_value = ShaderItem.use_material_texture
                NodeGroup.inputs.get("albedo_blend").default_value = ShaderItem.albedo_blend            
                NodeGroup.inputs.get("analytical_specular_contribution").default_value = ShaderItem.analytical_specular_contribution
            elif(ShaderItem.material_model_option == 2): #H3Category: material_model - two_lobe_phong
                NodeGroup.inputs.get("diffuse_coefficient").default_value = ShaderItem.diffuse_coefficient   
                NodeGroup.inputs.get("specular_coefficient").default_value = ShaderItem.specular_coefficient
                NodeGroup.inputs.get("normal_specular_power").default_value = ShaderItem.normal_specular_power
                NodeGroup.inputs.get("normal_specular_tint").default_value = ShaderItem.normal_specular_tint
                NodeGroup.inputs.get("glancing_specular_power").default_value = ShaderItem.glancing_specular_power
                NodeGroup.inputs.get("glancing_specular_tint").default_value = ShaderItem.glancing_specular_tint
                NodeGroup.inputs.get("fresnel_curve_steepness").default_value = ShaderItem.fresnel_curve_steepness
                NodeGroup.inputs.get("environment_map_specular_contribution").default_value = ShaderItem.environment_map_specular_contribution
                NodeGroup.inputs.get("albedo_specular_tint_blend").default_value = ShaderItem.albedo_specular_tint_blend   
                NodeGroup.inputs.get("analytical_specular_contribution").default_value = ShaderItem.analytical_specular_contribution            
            elif(ShaderItem.material_model_option == 5): #H3Category: material_model - glass
                NodeGroup.inputs.get("diffuse_coefficient").default_value = ShaderItem.diffuse_coefficient   
                NodeGroup.inputs.get("specular_coefficient").default_value = ShaderItem.specular_coefficient
                NodeGroup.inputs.get("roughness").default_value = ShaderItem.roughness
                NodeGroup.inputs.get("fresnel_coefficient").default_value = ShaderItem.fresnel_coefficient              
                NodeGroup.inputs.get("fresnel_curve_steepness").default_value = ShaderItem.fresnel_curve_steepness
                NodeGroup.inputs.get("fresnel_curve_bias").default_value = ShaderItem.fresnel_curve_bias                
                NodeGroup.inputs.get("analytical_specular_contribution").default_value = ShaderItem.analytical_specular_contribution            
            elif(ShaderItem.material_model_option == 7): #H3Category: material_model - single_lobe_phong
                NodeGroup.inputs.get("diffuse_coefficient").default_value = ShaderItem.diffuse_coefficient
                NodeGroup.inputs.get("specular_coefficient").default_value = ShaderItem.specular_coefficient        
                NodeGroup.inputs.get("specular_tint").default_value = ShaderItem.specular_tint    
                NodeGroup.inputs.get("roughness").default_value = ShaderItem.roughness            
                NodeGroup.inputs.get("environment_map_specular_contribution").default_value = ShaderItem.environment_map_specular_contribution
                NodeGroup.inputs.get("analytical_specular_contribution").default_value = ShaderItem.analytical_specular_contribution
                    
        #self illum group
        elif(category == "self illum"):
            if(ShaderItem.self_illumination_option == 1): #H3Category: self_illumination - simple
                NodeGroup.inputs.get("self_illum_color").default_value = ShaderItem.self_illum_color
                NodeGroup.inputs.get("self_illum_intensity").default_value = ShaderItem.self_illum_intensity            
            elif(ShaderItem.self_illumination_option == 2): #H3Category: self_illumination - 3_channel_self_illum
                NodeGroup.inputs.get("channel_a").default_value = ShaderItem.channel_a
                NodeGroup.inputs.get("channel_a_alpha").default_value = ShaderItem.channel_a_alpha
                NodeGroup.inputs.get("channel_b").default_value = ShaderItem.channel_b
                NodeGroup.inputs.get("channel_b_alpha").default_value = ShaderItem.channel_b_alpha
                NodeGroup.inputs.get("channel_c").default_value = ShaderItem.channel_c
                NodeGroup.inputs.get("channel_c_alpha").default_value = ShaderItem.channel_c_alpha            
            elif(ShaderItem.self_illumination_option == 3): #H3Category: self_illumination - plasma
                NodeGroup.inputs.get("color_wide").default_value = ShaderItem.color_wide
                NodeGroup.inputs.get("color_wide_alpha").default_value = ShaderItem.color_wide_alpha
                NodeGroup.inputs.get("color_sharp").default_value = ShaderItem.color_sharp
                NodeGroup.inputs.get("color_sharp_alpha").default_value = ShaderItem.color_sharp_alpha
                NodeGroup.inputs.get("color_medium").default_value = ShaderItem.color_medium
                NodeGroup.inputs.get("color_medium_alpha").default_value = ShaderItem.color_medium_alpha
                NodeGroup.inputs.get("self_illum_intensity").default_value = ShaderItem.self_illum_intensity
                NodeGroup.inputs.get("thinness_medium").default_value = ShaderItem.thinness_medium
                NodeGroup.inputs.get("thinness_wide").default_value = ShaderItem.thinness_wide
                NodeGroup.inputs.get("thinness_sharp").default_value = ShaderItem.thinness_sharp
            elif(ShaderItem.self_illumination_option == 4): #H3Category: self_illumination - from_diffuse
                NodeGroup.inputs.get("self_illum_color").default_value = ShaderItem.self_illum_color
                NodeGroup.inputs.get("self_illum_intensity").default_value = ShaderItem.self_illum_intensity
            elif(ShaderItem.self_illumination_option == 5): #H3Category: self_illumination - illum_detail
                NodeGroup.inputs.get("self_illum_color").default_value = ShaderItem.self_illum_color
                NodeGroup.inputs.get("self_illum_intensity").default_value = ShaderItem.self_illum_intensity
            elif(ShaderItem.self_illumination_option == 6): #H3Category: self_illumination - meter
                NodeGroup.inputs.get("meter_color_off").default_value = ShaderItem.meter_color_off
                NodeGroup.inputs.get("meter_color_on").default_value = ShaderItem.meter_color_on
                NodeGroup.inputs.get("meter_value").default_value = ShaderItem.meter_value
            elif(ShaderItem.self_illumination_option == 7): #H3Category: self_illumination - self_illum_times_diffuse
                NodeGroup.inputs.get("self_illum_color").default_value = ShaderItem.self_illum_color
                NodeGroup.inputs.get("self_illum_intensity").default_value = ShaderItem.self_illum_intensity
                NodeGroup.inputs.get("primary_change_color_blend").default_value = ShaderItem.primary_change_color_blend
            elif(Shader_Type == 3 and ShaderItem.self_illumination_option == 8): #H3Category: self_illumination - multilayer_additive
                #add these in later
                print("self_illumination - multilayer_additive")
            elif(Shader_Type == 3 and ShaderItem.self_illumination_option == 9): #H3Category: self_illumination - scope_blur
                #add these in later
                print("self_illumination - scope_blur")
            elif(Shader_Type == 3 and ShaderItem.self_illumination_option == 10): #H3Category: self_illumination - ml_add_four_change_color
                #add these in later
                print("self_illumination - ml_add_four_change_color")
            elif(Shader_Type == 3 and ShaderItem.self_illumination_option == 11): #H3Category: self_illumination - ml_add_five_change_color
                #add these in later
                print("self_illumination - ml_add_five_change_color")
            elif(Shader_Type == 3 and ShaderItem.self_illumination_option == 12): #H3Category: self_illumination - plasma_wide_and_sharp_five_change_color
                #add these in later
                print("self_illumination - plasma_wide_and_sharp_five_change_color")
            elif(Shader_Type == 3 and ShaderItem.self_illumination_option == 13): #H3Category: self_illumination - self_illum_holograms
                #add these in later
                print("self_illumination - self_illum_holograms")
            
            
            
            
            
        ##############    
        #terrain group
        ##############
        
        #Halo3TerrainCategory - material - diffuse_only
        #material 0
        #elif(category == "terrain1_m0"):             
            #no values for this group
        #material 1
        #elif(category == "terrain1_m1"):             
            #no values for this group
        #material 2
        #elif(category == "terrain1_m2"):             
            #no values for this group
        #material 3
        #elif(category == "terrain1_m3"):             
            #no values for this group

        #Halo3TerrainCategory - material - diffuse_plus_specular
        #all materials
        elif(category == "terrain"):
            NodeGroup.inputs.get("diffuse_coefficient_m_0").default_value = ShaderItem.diffuse_coefficient_m_0
            NodeGroup.inputs.get("specular_coefficient_m_0").default_value = ShaderItem.specular_coefficient_m_0
            NodeGroup.inputs.get("specular_power_m_0").default_value = ShaderItem.specular_power_m_0
            NodeGroup.inputs.get("specular_tint_m_0").default_value = ShaderItem.specular_tint_m_0
            NodeGroup.inputs.get("analytical_specular_contribution_m_0").default_value = ShaderItem.analytical_specular_contribution_m_0
            NodeGroup.inputs.get("fresnel_curve_steepness_m_0").default_value = ShaderItem.fresnel_curve_steepness_m_0
            NodeGroup.inputs.get("environment_specular_contribution_m_0").default_value = ShaderItem.environment_specular_contribution_m_0
            NodeGroup.inputs.get("albedo_specular_tint_blend_m_0").default_value = ShaderItem.albedo_specular_tint_blend_m_0
            NodeGroup.inputs.get("diffuse_coefficient_m_1").default_value = ShaderItem.diffuse_coefficient_m_1
            NodeGroup.inputs.get("specular_coefficient_m_1").default_value = ShaderItem.specular_coefficient_m_1
            NodeGroup.inputs.get("specular_power_m_1").default_value = ShaderItem.specular_power_m_1
            NodeGroup.inputs.get("specular_tint_m_1").default_value = ShaderItem.specular_tint_m_1
            NodeGroup.inputs.get("analytical_specular_contribution_m_1").default_value = ShaderItem.analytical_specular_contribution_m_1
            NodeGroup.inputs.get("fresnel_curve_steepness_m_1").default_value = ShaderItem.fresnel_curve_steepness_m_1
            NodeGroup.inputs.get("environment_specular_contribution_m_1").default_value = ShaderItem.environment_specular_contribution_m_1
            NodeGroup.inputs.get("albedo_specular_tint_blend_m_1").default_value = ShaderItem.albedo_specular_tint_blend_m_1    
            NodeGroup.inputs.get("diffuse_coefficient_m_2").default_value = ShaderItem.diffuse_coefficient_m_2
            NodeGroup.inputs.get("specular_coefficient_m_2").default_value = ShaderItem.specular_coefficient_m_2
            NodeGroup.inputs.get("specular_power_m_2").default_value = ShaderItem.specular_power_m_2
            NodeGroup.inputs.get("specular_tint_m_2").default_value = ShaderItem.specular_tint_m_2
            NodeGroup.inputs.get("analytical_specular_contribution_m_2").default_value = ShaderItem.analytical_specular_contribution_m_2
            NodeGroup.inputs.get("fresnel_curve_steepness_m_2").default_value = ShaderItem.fresnel_curve_steepness_m_2
            NodeGroup.inputs.get("environment_specular_contribution_m_2").default_value = ShaderItem.environment_specular_contribution_m_2
            NodeGroup.inputs.get("albedo_specular_tint_blend_m_2").default_value = ShaderItem.albedo_specular_tint_blend_m_2    
            NodeGroup.inputs.get("diffuse_coefficient_m_3").default_value = ShaderItem.diffuse_coefficient_m_3
            NodeGroup.inputs.get("specular_coefficient_m_3").default_value = ShaderItem.specular_coefficient_m_3
            NodeGroup.inputs.get("specular_power_m_3").default_value = ShaderItem.specular_power_m_3
            NodeGroup.inputs.get("specular_tint_m_3").default_value = ShaderItem.specular_tint_m_3
            NodeGroup.inputs.get("analytical_specular_contribution_m_3").default_value = ShaderItem.analytical_specular_contribution_m_3
            NodeGroup.inputs.get("fresnel_curve_steepness_m_3").default_value = ShaderItem.fresnel_curve_steepness_m_3
            NodeGroup.inputs.get("environment_specular_contribution_m_3").default_value = ShaderItem.environment_specular_contribution_m_3
            NodeGroup.inputs.get("albedo_specular_tint_blend_m_3").default_value = ShaderItem.albedo_specular_tint_blend_m_3

            #disable certain values if materials are off or are certain values
            if(ShaderItem.material_0_option == 0 or ShaderItem.material_0_option == 2 or ShaderItem.material_0_option == 3): #if off or diffuse only
                NodeGroup.inputs.get("specular_coefficient_m_0").default_value = 0.00
            elif(ShaderItem.material_1_option == 0 or ShaderItem.material_1_option == 2 or ShaderItem.material_1_option == 3): #if off or diffuse only
                NodeGroup.inputs.get("specular_coefficient_m_1").default_value = 0.00            
            elif(ShaderItem.material_2_option == 0 or ShaderItem.material_2_option == 2 or ShaderItem.material_2_option == 3): #if off or diffuse only
                NodeGroup.inputs.get("specular_coefficient_m_2").default_value = 0.00
            elif(ShaderItem.material_3_option == 0 or ShaderItem.material_3_option == 1): #if off or diffuse only
                NodeGroup.inputs.get("specular_coefficient_m_3").default_value = 0.00


        
        elif(category == "terrain2_m0"): 
            #print("applying values to m0")
            NodeGroup.inputs.get("diffuse_coefficient").default_value = ShaderItem.diffuse_coefficient_m_0
            NodeGroup.inputs.get("specular_coefficient").default_value = ShaderItem.specular_coefficient_m_0
            NodeGroup.inputs.get("specular_power").default_value = ShaderItem.specular_power_m_0
            NodeGroup.inputs.get("specular_tint").default_value = ShaderItem.specular_tint_m_0
            NodeGroup.inputs.get("analytical_specular_contribution").default_value = ShaderItem.analytical_specular_contribution_m_0
            NodeGroup.inputs.get("fresnel_curve_steepness").default_value = ShaderItem.fresnel_curve_steepness_m_0
            NodeGroup.inputs.get("environment_specular_contribution").default_value = ShaderItem.environment_specular_contribution_m_0
            NodeGroup.inputs.get("albedo_specular_tint_blend").default_value = ShaderItem.albedo_specular_tint_blend_m_0
        #material 1
        elif(category == "terrain2_m1"):   
            #print("applying values to m1")
            NodeGroup.inputs.get("diffuse_coefficient").default_value = ShaderItem.diffuse_coefficient_m_1
            NodeGroup.inputs.get("specular_coefficient").default_value = ShaderItem.specular_coefficient_m_1
            NodeGroup.inputs.get("specular_power").default_value = ShaderItem.specular_power_m_1
            NodeGroup.inputs.get("specular_tint").default_value = ShaderItem.specular_tint_m_1
            NodeGroup.inputs.get("analytical_specular_contribution").default_value = ShaderItem.analytical_specular_contribution_m_1
            NodeGroup.inputs.get("fresnel_curve_steepness").default_value = ShaderItem.fresnel_curve_steepness_m_1
            NodeGroup.inputs.get("environment_specular_contribution").default_value = ShaderItem.environment_specular_contribution_m_1
            NodeGroup.inputs.get("albedo_specular_tint_blend").default_value = ShaderItem.albedo_specular_tint_blend_m_1    
        #material 2
        elif(category == "terrain2_m2"):      
            #print("applying values to m2")    
            NodeGroup.inputs.get("diffuse_coefficient").default_value = ShaderItem.diffuse_coefficient_m_2
            NodeGroup.inputs.get("specular_coefficient").default_value = ShaderItem.specular_coefficient_m_2
            NodeGroup.inputs.get("specular_power").default_value = ShaderItem.specular_power_m_2
            NodeGroup.inputs.get("specular_tint").default_value = ShaderItem.specular_tint_m_2
            NodeGroup.inputs.get("analytical_specular_contribution").default_value = ShaderItem.analytical_specular_contribution_m_2
            NodeGroup.inputs.get("fresnel_curve_steepness").default_value = ShaderItem.fresnel_curve_steepness_m_2
            NodeGroup.inputs.get("environment_specular_contribution").default_value = ShaderItem.environment_specular_contribution_m_2
            NodeGroup.inputs.get("albedo_specular_tint_blend").default_value = ShaderItem.albedo_specular_tint_blend_m_2
        #material 3
        elif(category == "terrain2_m3"):  
            #print("applying values to m3")    
            NodeGroup.inputs.get("diffuse_coefficient").default_value = ShaderItem.diffuse_coefficient_m_3
            NodeGroup.inputs.get("specular_coefficient").default_value = ShaderItem.specular_coefficient_m_3
            NodeGroup.inputs.get("specular_power").default_value = ShaderItem.specular_power_m_3
            NodeGroup.inputs.get("specular_tint").default_value = ShaderItem.specular_tint_m_3
            NodeGroup.inputs.get("analytical_specular_contribution").default_value = ShaderItem.analytical_specular_contribution_m_3
            NodeGroup.inputs.get("fresnel_curve_steepness").default_value = ShaderItem.fresnel_curve_steepness_m_3
            NodeGroup.inputs.get("environment_specular_contribution").default_value = ShaderItem.environment_specular_contribution_m_3
            NodeGroup.inputs.get("albedo_specular_tint_blend").default_value = ShaderItem.albedo_specular_tint_blend_m_3
            
        return NodeGroup
    
       




    #MERGE DUPLICATE MATERIAL NAMES
    def merge_materials_on_objects(objects, materials):
        # Sort materials by name
        materials_sorted = sorted(materials, key=lambda m: m.name)

        # Find materials with the same name and merge them
        for obj in objects:
            material_slots = [slot for slot in obj.material_slots if slot.material is not None and not slot.is_property_readonly('material')]
            for slot in material_slots:
                material = slot.material
                material_name = material.name[:-4] if re.match('.*.\d{3}$', material.name) else material.name
                material_name_escaped = re.escape(material_name)
                material_cond = re.compile('^' + material_name_escaped + '$|^' + material_name_escaped + '.\d{3}$')
                material_to_change = next(iter([m for m in materials_sorted if re.match(material_cond, m.name)]), None)
                if material_to_change and material != material_to_change:
                    slot.material = material_to_change
                    

    merge_materials_on_objects(bpy.data.objects, bpy.data.materials)

                                        #################
                                        #START OF PROGRAM 
                                        #################    
    #get material count for the progress bar
    total_mats = len(bpy.data.materials)
    
    #assign progress bar
    wm = bpy.context.window_manager
    wm.progress_begin(0, total_mats)
    
    #mat = bpy.data.materials[999]                                    
                                        
    pymat = bpy.data.materials
    for idx, i in enumerate(pymat):
        #print ( 'i=',i)
        ShaderName = i.name + ".shader"                        # Shader_Type = 0
        ShaderName_Terrain_Shader = i.name + ".shader_terrain" # Shader_Type = 1
        ShaderName_Foliage_Shader = i.name + ".shader_foliage" # Shader_Type = 2
        ShaderName_Halogram_Shader = i.name + ".shader_halogram" # Shader_Type = 3
        ShaderPath = ""
        ShaderItem = shader() 
        Shader_Type = 0   #resets Shader_Type back to 0
        
        
        #Try to hansle multiple shader files of the same name
        file_found = False
        
        pymat_copy = i
       
        #update the progress bar
        wm.progress_update(idx)
        
        
        #find shader files and deal with each one
        for root, dirs, files in os.walk(Tag_Root):
            if (ShaderName_Terrain_Shader in files):
                ShaderName = ShaderName_Terrain_Shader
                Shader_Type = 1
                print("Terrain Shader Found!")
            elif (ShaderName_Foliage_Shader in files):
                ShaderName = ShaderName_Foliage_Shader
                Shader_Type = 2
                print("Foliage Shader Found!")
            # elif (ShaderName_Halogram_Shader in files):
                # ShaderName = ShaderName_Halogram_Shader
                # Shader_Type = 3
                # print("Halogram Shader Found!")
            

            if (ShaderName in files):
            
                if (file_found == True):
                    #create a new material with the same name but add a suffix to it and append it to pymat
                    #copy all this new data to that newly created material
                    
                    # If multiple files found, add a suffix to the material name
                    suffix = '.' + str(pymat.find(i.name) + 1).zfill(3)
                    pymat_copy = i.copy()
                    pymat_copy.name = i.name + suffix
                    pymat_copy = pymat.new(name=pymat_copy.name) 
                    print("Creating new Material in scene: " + pymat_copy.name)
                    #break
                    
                    #retargets i to be the newly created material
                    #i = pymat_copy #this might need to go at the end of the script
                    
                else:
                    print("first shader file")
                    #first iteration, do nothing
                    
                file_found = True #shader file wqs found
            
            
            
            
                print("------------New Shader-----------")
                print("")
                print("--[Shader Name]--")
                print(ShaderName)
                print("")
                
                #creates a blank Shader class object and clears data before each iteration
                ShaderItem = shader() 
                ShaderItem.name = ""
                ShaderItem.directory = ""
                ShaderItem.bitmap_count = 0
                ShaderItem.albedo_option = 0
                ShaderItem.bump_mapping_option = 0
                ShaderItem.alpha_test_option = 0
                ShaderItem.specular_mask_option = 0
                ShaderItem.material_model_option = 0
                ShaderItem.environment_mapping_option = 0
                ShaderItem.self_illumination_option = 0
                ShaderItem.blend_mode_option = 0
                ShaderItem.parallax_option = 0
                ShaderItem.misc_option = 0
                ShaderItem.bitmap_list = []
                ShaderItem.function_list = []
                ShaderItem.needed_bitmaps = []
                
                #used for default textures
                #Clear the found texture offsets for each new ShaderItem
                ShaderItem.BaseMap_Offset = 0x0
                ShaderItem.DetailMap_Offset = 0x0
                ShaderItem.DetailMap2_Offset = 0x0
                ShaderItem.DetailMap3_Offset = 0x0
                ShaderItem.SpecularMaskTexture_Offset = 0x0
                ShaderItem.ChangeColorMap_Offset = 0x0
                ShaderItem.BumpMap_Offset = 0x0
                ShaderItem.BumpDetailMap_Offset = 0x0
                ShaderItem.EnvironmentMap_Offset = 0x0
                ShaderItem.FlatEnvironmentMap_Offset = 0x0
                ShaderItem.SelfIllumMap_Offset = 0x0
                ShaderItem.SelfIllumDetailMap_Offset = 0x0
                
                
                
                
                
                #create blank function object
                FunctionItem = function()
                FunctionItem.tsgt_offset = 0x0
                FunctionItem.option = 0
                FunctionItem.range_toggle = False
                FunctionItem.function_name = ""
                FunctionItem.range_name = ""
                FunctionItem.time_period = 0.00
                FunctionItem.main_min_value = 0.00
                FunctionItem.main_max_value = 0.00
                FunctionItem.left_function_option = 0
                FunctionItem.left_frequency_value = 0.00
                FunctionItem.left_phase_value = 0.00
                FunctionItem.left_min_value = 0.00
                FunctionItem.left_max_value = 0.00
                FunctionItem.left_exponent_value = 0.00
                FunctionItem.right_function_option = 0
                FunctionItem.right_frequency_value = 0.00
                FunctionItem.right_phase_value = 0.00
                FunctionItem.right_min_value = 0.00
                FunctionItem.right_max_value = 0.00
                FunctionItem.right_exponent_value = 0.00
                
                ShaderOutputCount = 0
                ShadersConnected = 0
                BitmapCount = 10
                ImageTextureNodeList = []
                ImageTextureNodeList = [BitmapCount] #store all image texture nodes
                ShaderGroupList = [1] # used for keeping track of the order of the shader groups created
                
                
                #offsets for the shader
                CategoryOptions_Offset = 0x0
                BaseMap_Offset = 0x0
                #BaseMap2_Offset = 0x0    #for terrain shader later on
                DetailMap_Offset = 0x0
                DetailMap2_Offset = 0x0
                DetailMap3_Offset = 0x0
                SpecularMaskTexture_Offset = 0x0
                ChangeColorMap_Offset = 0x0
                BumpMap_Offset = 0x0
                BumpDetailMap_Offset = 0x0
                EnvironmentMap_Offset = 0x0
                FlatEnvironmentMap_Offset = 0x0
                SelfIllumMap_Offset = 0x0
                SelfIllumDetailMap_Offset = 0x0
                
                #offset for Alpha_Test_Map
                AlphaTestMap_Offset = 0x0
                
                #Offsets for values, scales and colors
                Albedo_Blend_Offset = 0x0
                Albedo_Color_Offset = 0x0
                Albedo_Color_Alpha_Offset = 0x0
                Bump_Detail_Coefficient_Offset = 0x0
                Env_Tint_Color_Offset  = 0x0
                Env_Roughness_Scale_Offset = 0x0
                Self_Illum_Color_Offset = 0x0
                Self_Illum_Intensity_Offset  = 0x0
                Channel_A_Offset  = 0x0
                Channel_A_Alpha_Offset = 0x0
                Channel_B_Offset  = 0x0
                Channel_B_Alpha_Offset  = 0x0
                Channel_C_Offset  = 0x0
                Channel_C_Alpha_Offset  = 0x0
                Color_Medium_Offset  = 0x0
                Color_Medium_Alpha_Offset  = 0x0
                Color_Wide_Offset  = 0x0
                Color_Wide_Alpha_Offset  = 0x0
                Color_Sharp_Offset  = 0x0
                Color_Sharp_Alpha_Offset  = 0x0
                Thinness_Medium_Offset  = 0x0
                Thinness_Wide_Offset = 0x0
                Thinness_Sharp_Offset  = 0x0
                Meter_Color_On_Offset  = 0x0
                Meter_Color_Off_Offset  = 0x0
                Meter_Value_Offset  = 0x0
                Primary_Change_Color_blend_Offset  = 0x0
                Height_Scale_Offset  = 0x0
                Diffuse_Coefficient_Offset = 0x0
                Specular_Coefficient_Offset  = 0x0
                Specular_Tint_Offset  = 0x0
                Fresnel_Color_Offset  = 0x0
                Roughness_Offset  = 0x0
                Environment_Map_Specular_Contribution_Offset = 0x0 
                Use_Material_Texture_Offset  = 0x0
                Normal_Specular_Power_Offset  = 0x0
                Normal_Specular_Tint_Offset  = 0x0
                Glancing_Specular_Power_Offset  = 0x0
                Glancing_Specular_Tint_Offset  = 0x0
                Fresnel_Curve_Steepness_Offset = 0x0
                Albedo_Specular_Tint_Blend_Offset  = 0x0
                Fresnel_Curve_Bias_Offset = 0x0
                Fresnel_Coefficient_Offset = 0x0
                Analytical_Specular_Contribution_Offset = 0x0

                #terrain shaders stuff
                #bitmaps
                Terrain_Options_Offset = 0x0
                Blend_Map_Offset = 0x0

                Base_Map_M_0_Offset = 0x0
                Detail_Map_M_0_Offset = 0x0
                Bump_Map_M_0_Offset = 0x0
                Detail_Bump_M_0_Offset = 0x0
                
                Base_Map_M_1_Offset = 0x0
                Detail_Map_M_1_Offset = 0x0
                Bump_Map_M_1_Offset = 0x0
                Detail_Bump_M_1_Offset = 0x0
                
                Base_Map_M_2_Offset = 0x0
                Detail_Map_M_2_Offset = 0x0
                Bump_Map_M_2_Offset = 0x0
                Detail_Bump_M_2_Offset = 0x0
                
                Base_Map_M_3_Offset = 0x0
                Detail_Map_M_3_Offset = 0x0
                Bump_Map_M_3_Offset = 0x0
                Detail_Bump_M_3_Offset = 0x0
                
                
                #colors/values etc
                Global_Albedo_Tint_Offset = 0x0
                
                Diffuse_Coefficient_M_0_Offset = 0x0
                Specular_Coefficient_M_0_Offset = 0x0
                Specular_Power_M_0_Offset = 0x0
                Specular_Tint_M_0_Offset = 0x0
                Fresnel_Curve_Steepness_M_0_Offset = 0x00
                Area_Specular_Contribution_M_0_Offset = 0x0
                Analytical_Specular_Contribution_M_0_Offset = 0x0
                Environment_Specular_Contribution_M_0_Offset = 0x0
                Albedo_Specular_Tint_Blend_M_0_Offset = 0x0
                
                Diffuse_Coefficient_M_1_Offset = 0x0
                Specular_Coefficient_M_1_Offset = 0x0
                Specular_Power_M_1_Offset = 0x0
                Specular_Tint_M_1_Offset = 0x0
                Fresnel_Curve_Steepness_M_1_Offset = 0x0
                Area_Specular_Contribution_M_1_Offset = 0x0
                Analytical_Specular_Contribution_M_1_Offset = 0x0
                Environment_Specular_Contribution_M_1_Offset = 0x0
                Albedo_Specular_Tint_Blend_M_1_Offset = 0x0
                
                Diffuse_Coefficient_M_2_Offset = 0x0
                Specular_Coefficient_M_2_Offset = 0x0
                Specular_Power_M_2_Offset = 0x0
                Specular_Tint_M_2_Offset = 0x0
                Fresnel_Curve_Steepness_M_2_Offset = 0x0
                Area_Specular_Contribution_M_2_Offset = 0x0
                Analytical_Specular_Contribution_M_2_Offset = 0x0
                Environment_Specular_Contribution_M_2_Offset = 0x0
                Albedo_Specular_Tint_Blend_M_2_Offset = 0x0
                
                Diffuse_Coefficient_M_3_Offset = 0x0
                Specular_Coefficient_M_3_Offset = 0x0
                Specular_Power_M_3_Offset = 0x0
                Specular_Tint_M_3_Offset = 0x0
                Fresnel_Curve_Steepness_M_3_Offset = 0x0
                Area_Specular_Contribution_M_3_Offset = 0x0
                Analytical_Specular_Contribution_M_3_Offset = 0x0
                Environment_Specular_Contribution_M_3_Offset = 0x0
                Albedo_Specular_Tint_Blend_M_3_Offset = 0x0
                        
                #Halogram shaders
                Halogram_Options_Offset = 0x0
                        
                        
                        
                ShaderPath = root + "/" + ShaderName
                print ("Shader exists!")
                
                print("")
                print("--[Shader Directory]--")
                print(ShaderPath)
                
                #open shader file in raw binary
                shaderfile = open(ShaderPath, "rb")
                shaderfile_read = shaderfile.read()
                
                print("")
                print("[Texture Types Not Found/Needed]")
                
                                            ################
                                            #FINDING OFFSETS
                                            ################
                ###################################
                # .shader files and foliage shaders
                ###################################
                
                #if shader file is .shader or foliage shaders
                if (Shader_Type == 0 or Shader_Type == 2):   #then search for this data below
                
                    #GET START OFFSETS FOR DATA FROM SHADER FILE              maybe add the crap after the type name tp make sure it is legit full type name IF lbgt is 12bytes after end of type name then no directory
                    try: 
                        CategoryOptions_Offset = shaderfile_read.index(b'\x73\x68\x61\x64\x65\x72\x73\x5C\x73\x68\x61\x64\x65\x72')
                    except ValueError:
                        if(debug_textures_values_found != 0):
                            print("Category Options not found!")
                    
                    #foliage
                    if(Shader_Type == 2):
                        try: 
                            CategoryOptions_Offset = shaderfile_read.index(b'\x73\x68\x61\x64\x65\x72\x73\x5C\x66\x6F\x6C\x69\x61\x67\x65\x6C\x62\x67\x74')
                        except ValueError:
                            if(debug_textures_values_found != 0):                        
                                print("Category Options not found!")                    

                    #halogram
                    if(Shader_Type == 3):
                        try: 
                            CategoryOptions_Offset = shaderfile_read.index(b'\x73\x68\x61\x64\x65\x72\x73\x5C\x68\x61\x6C\x6F\x67\x72\x61\x6D\x6C\x62\x67\x74')
                        except ValueError:
                            if(debug_textures_values_found != 0):                        
                                print("Category Options not found!") 
                    
                    #CHECK FOR TEXTURE OFFSETS    
                    try: #check for base_map
                        BaseMap_Offset = shaderfile_read.index(b'\x00\x62\x61\x73\x65\x5F\x6D\x61\x70\x66\x72\x67\x74')
                        ShaderItem.BaseMap_Offset = BaseMap_Offset
                    except ValueError:
                        if(debug_textures_values_found != 0):                        
                            print("base_map not found!")
                    try: 
                        DetailMap_Offset = shaderfile_read.index(b'\x00\x64\x65\x74\x61\x69\x6c\x5f\x6d\x61\x70\x66\x72\x67\x74')
                        ShaderItem.DetailMap_Offset = DetailMap_Offset
                    except ValueError:
                        if(debug_textures_values_found != 0):
                            print("detail_map not found!")
                    try: 
                        DetailMap2_Offset = shaderfile_read.index(b'\x00\x64\x65\x74\x61\x69\x6c\x5f\x6d\x61\x70\x32\x66\x72\x67\x74')
                        ShaderItem.DetailMap2_Offset = DetailMap2_Offset
                    except ValueError:
                        if(debug_textures_values_found != 0):
                            print("detail_map2 not found!")
                    try: 
                        DetailMap3_Offset = shaderfile_read.index(b'\x00\x64\x65\x74\x61\x69\x6c\x5f\x6d\x61\x70\x33\x66\x72\x67\x74')
                        ShaderItem.DetailMap3_Offset = DetailMap3_Offset
                    except ValueError:
                        if(debug_textures_values_found != 0):
                            print("detail_map3 not found!")
                    #search for detail_map_overlay                
                    try: 
                        SpecularMaskTexture_Offset = shaderfile_read.index(b'\x00\x73\x70\x65\x63\x75\x6C\x61\x72\x5F\x6D\x61\x73\x6B\x5F\x74\x65\x78\x74\x75\x72\x65\x66\x72\x67\x74')
                        ShaderItem.SpecularMaskTexture_Offset = SpecularMaskTexture_Offset
                    except ValueError:
                        if(debug_textures_values_found != 0):                    
                            print("specular_mask_texture not found!")    
                    try: 
                        ChangeColorMap_Offset = shaderfile_read.index(b'\x00\x63\x68\x61\x6e\x67\x65\x5f\x63\x6f\x6c\x6f\x72\x5f\x6d\x61\x70\x66\x72\x67\x74')
                        ShaderItem.ChangeColorMap_Offset = ChangeColorMap_Offset
                    except ValueError:
                        if(debug_textures_values_found != 0):                    
                            print("change_color_map not found!")
                    try: 
                        BumpMap_Offset = shaderfile_read.index(b'\x00\x62\x75\x6d\x70\x5f\x6d\x61\x70\x66\x72\x67\x74')
                        ShaderItem.BumpMap_Offset = BumpMap_Offset
                    except ValueError:
                        if(debug_textures_values_found != 0):                    
                            print("bump_map not found!")
                    try: 
                        BumpDetailMap_Offset = shaderfile_read.index(b'\x00\x62\x75\x6d\x70\x5f\x64\x65\x74\x61\x69\x6c\x5f\x6d\x61\x70\x66\x72\x67\x74')
                        ShaderItem.BumpDetailMap_Offset = BumpDetailMap_Offset
                    except ValueError:
                        if(debug_textures_values_found != 0):                    
                            print("bump_detail_map not found!")       
                    try: 
                        EnvironmentMap_Offset = shaderfile_read.index(b'\x00\x65\x6e\x76\x69\x72\x6f\x6e\x6d\x65\x6e\x74\x5f\x6d\x61\x70\x66\x72\x67\x74')
                        ShaderItem.EnvironmentMap_Offset = EnvironmentMap_Offset
                    except ValueError:
                        if(debug_textures_values_found != 0):                    
                            print("environment_map not found!")     
                    try: 
                        FlatEnvironmentMap_Offset = shaderfile_read.index(b'\x00\x66\x6C\x61\x74\x5F\x65\x6E\x76\x69\x72\x6F\x6E\x6D\x65\x6E\x74\x5F\x6D\x61\x70\x66\x72\x67\x74')
                        ShaderItem.FlatEnvironmentMap_Offset = FlatEnvironmentMap_Offset
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("flat_environment_map not found!")     
                    try: 
                        SelfIllumMap_Offset = shaderfile_read.index(b'\x00\x73\x65\x6c\x66\x5f\x69\x6c\x6c\x75\x6d\x5f\x6d\x61\x70\x66\x72\x67\x74')
                        ShaderItem.SelfIllumMap_Offset = SelfIllumMap_Offset
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("self_illum_map not found!")     
                    try: 
                        SelfIllumDetailMap_Offset = shaderfile_read.index(b'\x00\x73\x65\x6c\x66\x5f\x69\x6c\x6c\x75\x6d\x5f\x64\x65\x74\x61\x69\x6c\x5f\x6d\x61\x70\x66\x72\x67\x74')
                        ShaderItem.SelfIllumDetailMap_Offset = SelfIllumDetailMap_Offset
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("self_illum_detail_map not found!")

                    #Check for Alpha_Map
                    try: 
                        AlphaTestMap_Offset = shaderfile_read.index(b'\x00\x61\x6C\x70\x68\x61\x5F\x74\x65\x73\x74\x5F\x6D\x61\x70\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("alpha_test_map not found!")

                    #CHECK FOR SCALE, COLOR, AND VALUE  
                    try: 
                        Albedo_Blend_Offset = shaderfile_read.index(b'\x00\x61\x6C\x62\x65\x64\x6F\x5F\x62\x6C\x65\x6E\x64\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("albedo_blend not found!")
                    try: 
                        Albedo_Color_Offset = shaderfile_read.index(b'\x00\x61\x6c\x62\x65\x64\x6f\x5f\x63\x6f\x6c\x6f\x72\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("albedo_color not found!")
                    try: 
                        Albedo_Color_Alpha_Offset = shaderfile_read.index(b'\x00\x61\x6c\x62\x65\x64\x6f\x5f\x63\x6f\x6c\x6f\x72\x5f\x61\x6c\x70\x68\x61\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("albedo_color_alpha not found!")    
                    try: 
                        Bump_Detail_Coefficient_Offset = shaderfile_read.index(b'\x00\x62\x75\x6d\x70\x5f\x64\x65\x74\x61\x69\x6c\x5f\x63\x6f\x65\x66\x66\x69\x63\x69\x65\x6e\x74\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("bump_detail_coefficient not found!")    
                    try: 
                        Env_Tint_Color_Offset = shaderfile_read.index(b'\x00\x65\x6e\x76\x5f\x74\x69\x6e\x74\x5f\x63\x6f\x6c\x6f\x72\x66\x72\x67\x74')
                        
                        #IF FOR SOME GOD AWFUL REASON THERE IS A SECOND COLOR VALUE THEN THIS WILL GRAB THAT INSTEAD
                        if (test_find(Env_Tint_Color_Offset, shaderfile, "env_tint_color") != -1):
                            Env_Tint_Color_Offset = test_find(Env_Tint_Color_Offset, shaderfile, "env_tint_color")
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("env_tint_color not found!")
                    try: 
                        Env_Roughness_Scale_Offset = shaderfile_read.index(b'\x00\x65\x6e\x76\x5f\x72\x6f\x75\x67\x68\x6e\x65\x73\x73\x5f\x73\x63\x61\x6c\x65\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("env_roughness_scale not found!")    
                    try: 
                        Self_Illum_Color_Offset = shaderfile_read.index(b'\x00\x73\x65\x6c\x66\x5f\x69\x6c\x6c\x75\x6d\x5f\x63\x6f\x6c\x6f\x72\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("self_illum_color not found!")    
                    try: 
                        Self_Illum_Intensity_Offset = shaderfile_read.index(b'\x00\x73\x65\x6c\x66\x5f\x69\x6c\x6c\x75\x6d\x5f\x69\x6e\x74\x65\x6e\x73\x69\x74\x79\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("self_illum_intensity not found!")    
                    try: 
                        Channel_A_Offset = shaderfile_read.index(b'\x00\x63\x68\x61\x6e\x6e\x65\x6c\x5f\x61\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("channel_a not found!")    
                    try: 
                        Channel_A_Alpha_Offset = shaderfile_read.index(b'\x00\x63\x68\x61\x6e\x6e\x65\x6c\x5f\x61\x5f\x61\x6c\x70\x68\x61\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("channel_a_alpha not found!")    
                    try: 
                        Channel_B_Offset = shaderfile_read.index(b'\x00\x63\x68\x61\x6e\x6e\x65\x6c\x5f\x62\x66\x72\x67\x74')
                    except ValueError:
                        if(Channel_A_Offset != 0):
                            #add default data
                            ShaderItem.channel_b = color_white_rgb
                            if(debug_textures_values_found != 0): 
                                print("channel_b not found, but others were. Adding default data to channel_b")
                        else:
                            ShaderItem.channel_b = color_white_rgb
                            if(debug_textures_values_found != 0): 
                                print("channel_b not found!")   
                    try: 
                        Channel_B_Alpha_Offset = shaderfile_read.index(b'\x00\x63\x68\x61\x6e\x6e\x65\x6c\x5f\x62\x5f\x61\x6c\x70\x68\x61\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("channel_b_alpha not found!")    
                    try: 
                        Channel_C_Offset = shaderfile_read.index(b'\x00\x63\x68\x61\x6e\x6e\x65\x6c\x5f\x63\x66\x72\x67\x74')
                    except ValueError:
                        if(Channel_A_Offset != 0 or Channel_B_Offset != 0):
                            #add default data
                            ShaderItem.channel_c = color_white_rgb
                            if(debug_textures_values_found != 0): 
                                print("channel_c not found, but others were. Adding default data to channel_c")
                        else:
                            if(debug_textures_values_found != 0): 
                                print("channel_c not found!")    
                    try: 
                        Channel_C_Alpha_Offset = shaderfile_read.index(b'\x00\x63\x68\x61\x6e\x6e\x65\x6c\x5f\x63\x5f\x61\x6c\x70\x68\x61\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("channel_c_alpha not found!")    
                    try: 
                        Color_Medium_Offset = shaderfile_read.index(b'\x00\x63\x6f\x6c\x6f\x72\x5f\x6d\x65\x64\x69\x75\x6d\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("color_medium not found!")    
                    try: 
                        Color_Medium_Alpha_Offset = shaderfile_read.index(b'\x00\x63\x6f\x6c\x6f\x72\x5f\x6d\x65\x64\x69\x75\x6d\x5f\x61\x6c\x70\x68\x61\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("color_medium_alpha not found!")    
                    try: 
                        Color_Wide_Offset = shaderfile_read.index(b'\x00\x63\x6f\x6c\x6f\x72\x5f\x77\x69\x64\x65\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("color_wide not found!")    
                    try: 
                        Color_Wide_Alpha_Offset = shaderfile_read.index(b'\x00\x63\x6f\x6c\x6f\x72\x5f\x77\x69\x64\x65\x5f\x61\x6c\x70\x68\x61\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("color_wide_alpha not found!")    
                    try: 
                        Color_Sharp_Offset = shaderfile_read.index(b'\x00\x63\x6f\x6c\x6f\x72\x5f\x73\x68\x61\x72\x70\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("color_sharp not found!")    
                    try: 
                        Color_Sharp_Alpha_Offset = shaderfile_read.index(b'\x00\x63\x6f\x6c\x6f\x72\x5f\x73\x68\x61\x72\x70\x5f\x61\x6c\x70\x68\x61\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("color_sharp_alpha not found!")    
                    try: 
                        Thinness_Medium_Offset = shaderfile_read.index(b'\x00\x74\x68\x69\x6e\x6e\x65\x73\x73\x5f\x6d\x65\x64\x69\x75\x6d\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("thinness_medium not found!")    
                    try: 
                        Thinness_Wide_Offset = shaderfile_read.index(b'\x00\x74\x68\x69\x6e\x6e\x65\x73\x73\x5f\x77\x69\x64\x65\x66\x72\x67x\74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("thinness_wide not found!")    
                    try: 
                        Thinness_Sharp_Offset = shaderfile_read.index(b'\x00\x74\x68\x69\x6e\x6e\x65\x73\x73\x5f\x73\x68\x61\x72\x70\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("thinness_sharp not found!")    
                    try: 
                        Meter_Color_On_Offset = shaderfile_read.index(b'\x00\x6d\x65\x74\x65\x72\x5f\x63\x6f\x6c\x6f\x72\x5f\x6f\x6e\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("meter_color_on not found!")    
                    try: 
                        Meter_Color_Off_Offset = shaderfile_read.index(b'\x00\x6d\x65\x74\x65\x72\x5f\x63\x6f\x6c\x6f\x72\x5f\x6f\x66\x66\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("meter_color_off not found!")    
                    try: 
                        Meter_Value_Offset = shaderfile_read.index(b'\x00\x6d\x65\x74\x65\x72\x5f\x76\x61\x6c\x75\x65\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("meter_value not found!")    
                    try: 
                        Primary_Change_Color_blend_Offset = shaderfile_read.index(b'\x00\x70\x72\x69\x6d\x61\x72\x79\x5f\x63\x68\x61\x6e\x67\x65\x5f\x63\x6f\x6c\x6f\x72\x5f\x62\x6c\x65\x6e\x64\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("primary_change_color_blend not found!")    
                    try: 
                        Height_Scale_Offset = shaderfile_read.index(b'\x00\x68\x65\x69\x67\x68\x74\x5f\x73\x63\x61\x6c\x65\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("height_scale not found!")    
                    try: 
                        Diffuse_Coefficient_Offset = shaderfile_read.index(b'\x00\x64\x69\x66\x66\x75\x73\x65\x5f\x63\x6f\x65\x66\x66\x69\x63\x69\x65\x6e\x74\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("diffuse_coefficient not found!")    
                    try: 
                        Specular_Coefficient_Offset = shaderfile_read.index(b'\x00\x73\x70\x65\x63\x75\x6c\x61\x72\x5f\x63\x6f\x65\x66\x66\x69\x63\x69\x65\x6e\x74\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("specular_coefficient not found!")    
                    try: 
                        Specular_Tint_Offset = shaderfile_read.index(b'\x00\x73\x70\x65\x63\x75\x6c\x61\x72\x5f\x74\x69\x6e\x74\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("specular_tint not found!")    
                    try: 
                        Fresnel_Color_Offset = shaderfile_read.index(b'\x00\x66\x72\x65\x73\x6e\x65\x6c\x5f\x63\x6f\x6c\x6f\x72\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("fresnel_color not found!")    
                    try: 
                        Roughness_Offset = shaderfile_read.index(b'\x00\x72\x6f\x75\x67\x68\x6e\x65\x73\x73\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("roughness not found!")    
                    try: 
                        Environment_Map_Specular_Contribution_Offset = shaderfile_read.index(b'\x00\x65\x6e\x76\x69\x72\x6f\x6e\x6d\x65\x6e\x74\x5f\x6d\x61\x70\x5f\x73\x70\x65\x63\x75\x6c\x61\x72\x5f\x63\x6f\x6e\x74\x72\x69\x62\x75\x74\x69\x6f\x6e\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("environment_map_specular_contribution not found!")    
                    try: 
                        Use_Material_Texture_Offset = shaderfile_read.index(b'\x00\x75\x73\x65\x5f\x6d\x61\x74\x65\x72\x69\x61\x6c\x5f\x74\x65\x78\x74\x75\x72\x65\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("use_material_texture not found!")    
                    try: 
                        Normal_Specular_Power_Offset = shaderfile_read.index(b'\x00\x6e\x6f\x72\x6d\x61\x6c\x5f\x73\x70\x65\x63\x75\x6c\x61\x72\x5f\x70\x6f\x77\x65\x72\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("normal_specular_power not found!")    
                    try: 
                        Normal_Specular_Tint_Offset = shaderfile_read.index(b'\x00\x6e\x6f\x72\x6d\x61\x6c\x5f\x73\x70\x65\x63\x75\x6c\x61\x72\x5f\x74\x69\x6e\x74\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("normal_specular_tint not found!")                #6E 6F 72 6D 61 6C 5F 73 70 65 63 75 6C 61 72 5F 74 69 6E 74
                    try: 
                        Glancing_Specular_Power_Offset = shaderfile_read.index(b'\x00\x67\x6c\x61\x6e\x63\x69\x6e\x67\x5f\x73\x70\x65\x63\x75\x6c\x61\x72\x5f\x70\x6f\x77\x65\x72\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("glancing_specular_power not found!")    
                    try: 
                        Glancing_Specular_Tint_Offset = shaderfile_read.index(b'\x00\x67\x6c\x61\x6e\x63\x69\x6e\x67\x5f\x73\x70\x65\x63\x75\x6c\x61\x72\x5f\x74\x69\x6e\x74\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("glancing_specular_tint not found!")                #67 6C 61 6E 63 69 6E 67 5F 73 70 65 63 75 6C 61 72 5F 74 69 6E 74
                    try: 
                        Fresnel_Curve_Steepness_Offset = shaderfile_read.index(b'\x00\x66\x72\x65\x73\x6e\x65\x6c\x5f\x63\x75\x72\x76\x65\x5f\x73\x74\x65\x65\x70\x6e\x65\x73\x73\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("fresnel_curve_steepness not found!")    
                    try: 
                        Albedo_Specular_Tint_Blend_Offset = shaderfile_read.index(b'\x00\x61\x6c\x62\x65\x64\x6f\x5f\x73\x70\x65\x63\x75\x6c\x61\x72\x5f\x74\x69\x6e\x74\x5f\x62\x6c\x65\x6e\x64\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("albedo_specular_tint_blend not found!")    
                    try: 
                        Fresnel_Curve_Bias_Offset_Offset = shaderfile_read.index(b'\x00\x66\x72\x65\x73\x6E\x65\x6C\x5F\x63\x75\x72\x76\x65\x5F\x62\x69\x61\x73\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("fresnel_curve_bias not found!")
                    try: 
                        Fresnel_Coefficient_Offset = shaderfile_read.index(b'\x00\x66\x72\x65\x73\x6E\x65\x6C\x5F\x63\x6F\x65\x66\x66\x69\x63\x69\x65\x6E\x74\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("fresnel_coefficient not found!")
                    try: 
                        Analytical_Specular_Contribution_Offset = shaderfile_read.index(b'\x00\x61\x6E\x61\x6C\x79\x74\x69\x63\x61\x6C\x5F\x73\x70\x65\x63\x75\x6C\x61\x72\x5F\x63\x6F\x6E\x74\x72\x69\x62\x75\x74\x69\x6F\x6E\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("analytical_specular_contribution not found!")            
                
        

                    #######################
                    #TERRAIN SHADER OFFSETS
                    #######################
                        
                #if shader file is .shader_terrain
                if (Shader_Type == 1):
                 
                    ###########
                    #Categories
                    ###########
                    
                    try: 
                        CategoryOptions_Offset = shaderfile_read.index(b'\x00\x66\x64\x6D\x72\x73\x68\x61\x64\x65\x72\x73\x5C\x74\x65\x72\x72\x61\x69\x6E\x6C\x62\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("Category Options not found!")
                    
                    #########
                    #Textures
                    #########
                    try: 
                        Blend_Map_Offset = shaderfile_read.index(b'\x00\x62\x6C\x65\x6E\x64\x5F\x6D\x61\x70\x66\x72\x67\x74') #
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("blend_map not found!")   
                    try: 
                        Base_Map_M_0_Offset = shaderfile_read.index(b'\x00\x62\x61\x73\x65\x5F\x6D\x61\x70\x5F\x6D\x5F\x30\x66\x72\x67\x74') #
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("base_map_m_0 not found!") 
                    try: 
                        Detail_Map_M_0_Offset = shaderfile_read.index(b'\x00\x64\x65\x74\x61\x69\x6C\x5F\x6D\x61\x70\x5F\x6D\x5F\x30\x66\x72\x67\x74') #
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("detail_map_m_0 not found!") 
                    try: 
                        Bump_Map_M_0_Offset = shaderfile_read.index(b'\x00\x62\x75\x6D\x70\x5F\x6D\x61\x70\x5F\x6D\x5F\x30\x66\x72\x67\x74') #
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("bump_map_m_0 not found!") 
                    try: 
                        Detail_Bump_M_0_Offset = shaderfile_read.index(b'\x00\x64\x65\x74\x61\x69\x6C\x5F\x62\x75\x6D\x70\x5F\x6D\x5F\x30\x66\x72\x67\x74') #
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("detail_bump_m_0 not found!") 
                    try: 
                        Base_Map_M_1_Offset = shaderfile_read.index(b'\x00\x62\x61\x73\x65\x5F\x6D\x61\x70\x5F\x6D\x5F\x31\x66\x72\x67\x74') #
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("base_map_m_1 not found!") 
                    try: 
                        Detail_Map_M_1_Offset = shaderfile_read.index(b'\x00\x64\x65\x74\x61\x69\x6C\x5F\x6D\x61\x70\x5F\x6D\x5F\x31\x66\x72\x67\x74')#
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("detail_map_m_1 not found!") 
                    try: 
                        Bump_Map_M_1_Offset = shaderfile_read.index(b'\x00\x62\x75\x6D\x70\x5F\x6D\x61\x70\x5F\x6D\x5F\x31\x66\x72\x67\x74') #
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("bump_map_m_1 not found!") 
                    try: 
                        Detail_Bump_M_1_Offset = shaderfile_read.index(b'\x00\x64\x65\x74\x61\x69\x6C\x5F\x6D\x61\x70\x5F\x6D\x5F\x31\x66\x72\x67\x74') #
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("detail_bump_m_1 not found!") 
                    try: 
                        Base_Map_M_2_Offset = shaderfile_read.index(b'\x00\x62\x61\x73\x65\x5F\x6D\x61\x70\x5F\x6D\x5F\x32\x66\x72\x67\x74') #
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("base_map_m_2 not found!") 
                    try: 
                        Detail_Map_M_2_Offset = shaderfile_read.index(b'\x00\x64\x65\x74\x61\x69\x6C\x5F\x6D\x61\x70\x5F\x6D\x5F\x32\x66\x72\x67\x74')#
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("detail_map_m_2 not found!") 
                    try: 
                        Bump_Map_M_2_Offset = shaderfile_read.index(b'\x00\x62\x75\x6D\x70\x5F\x6D\x61\x70\x5F\x6D\x5F\x32\x66\x72\x67\x74') #
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("bump_map_m_2 not found!") 
                    try: 
                        Detail_Bump_M_2_Offset = shaderfile_read.index(b'\x00\x64\x65\x74\x61\x69\x6C\x5F\x6D\x61\x70\x5F\x6D\x5F\x32\x66\x72\x67\x74') #
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("detail_bump_m_2 not found!") 
                    try:  
                        Base_Map_M_3_Offset = shaderfile_read.index(b'\x00\x62\x61\x73\x65\x5F\x6D\x61\x70\x5F\x6D\x5F\x33\x66\x72\x67\x74') #
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("base_map_m_3 not found!") 
                    try: 
                        Detail_Map_M_3_Offset = shaderfile_read.index(b'\x00\x64\x65\x74\x61\x69\x6C\x5F\x6D\x61\x70\x5F\x6D\x5F\x33\x66\x72\x67\x74') #
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("detail_map_m_3 not found!") 
                    try: 
                        Bump_Map_M_3_Offset = shaderfile_read.index(b'\x00\x62\x75\x6D\x70\x5F\x6D\x61\x70\x5F\x6D\x5F\x33\x66\x72\x67\x74') #
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("bump_map_m_3 not found!") 
                    try: 
                        Detail_Bump_M_3_Offset = shaderfile_read.index(b'\x00\x64\x65\x74\x61\x69\x6C\x5F\x6D\x61\x70\x5F\x6D\x5F\x33\x66\x72\x67\x74') #
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("detail_bump_m_3 not found!") 
                       
                    ##############
                    #COLORS/VALUES
                    ##############
                    
                    try: 
                        Global_Albedo_Tint_Offset = shaderfile_read.index(b'\x00\x67\x6C\x6F\x62\x61\x6C\x5F\x61\x6C\x62\x65\x64\x6F\x5F\x74\x69\x6E\x74\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("global_albedo_tint not found!")   
                    
                    try: 
                        Diffuse_Coefficient_M_0_Offset = shaderfile_read.index(b'\x00\x64\x69\x66\x66\x75\x73\x65\x5F\x63\x6F\x65\x66\x66\x69\x63\x69\x65\x6E\x74\x5F\x6D\x5F\x30\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("diffuse_coefficient_m_0 not found!")
                    try: 
                        Specular_Coefficient_M_0_Offset = shaderfile_read.index(b'\x00\x73\x70\x65\x63\x75\x6C\x61\x72\x5F\x63\x6F\x65\x66\x66\x69\x63\x69\x65\x6E\x74\x5F\x6D\x5F\x30\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("specular_coefficient_m_0 not found!")
                    try: 
                        Specular_Power_M_0_Offset = shaderfile_read.index(b'\x00\x73\x70\x65\x63\x75\x6C\x61\x72\x5F\x70\x6F\x77\x65\x72\x5F\x6D\x5F\x30\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("specular_power_m_0 not found!")
                    try: 
                        Specular_Tint_M_0_Offset = shaderfile_read.index(b'\x00\x73\x70\x65\x63\x75\x6C\x61\x72\x5F\x74\x69\x6E\x74\x5F\x6D\x5F\x30\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("specular_tint_m_0 not found!")
                    try: 
                        Fresnel_Curve_Steepness_M_0_Offset = shaderfile_read.index(b'\x00\x66\x72\x65\x73\x6e\x65\x6c\x5f\x63\x75\x72\x76\x65\x5f\x73\x74\x65\x65\x70\x6e\x65\x73\x73\x5f\x6d\x5f\x30\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("fresnel_curve_steepness_m_0 not found!")
                    try: 
                        Area_Specular_Contribution_M_0_Offset = shaderfile_read.index(b'\x00\x61\x72\x65\x61\x5F\x73\x70\x65\x63\x75\x6C\x61\x72\x5F\x63\x6F\x6E\x74\x72\x69\x62\x75\x74\x69\x6F\x6E\x5F\x6D\x5F\x30\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("area_specular_contribution_m_0 not found!")
                    try: 
                        Analytical_Specular_Contribution_M_0_Offset = shaderfile_read.index(b'\x00\x61\x6E\x61\x6C\x79\x74\x69\x63\x61\x6C\x5F\x73\x70\x65\x63\x75\x6C\x61\x72\x5F\x63\x6F\x6E\x74\x72\x69\x62\x75\x74\x69\x6F\x6E\x5F\x6D\x5F\x30\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("analytical_specular_contribution_m_0 not found!")
                    try: 
                        Environment_Specular_Contribution_M_0_Offset = shaderfile_read.index(b'\x00\x65\x6e\x76\x69\x72\x6f\x6e\x6d\x65\x6e\x74\x5f\x73\x70\x65\x63\x75\x6c\x61\x72\x5f\x63\x6f\x6e\x74\x72\x69\x62\x75\x74\x69\x6f\x6e\x5f\x6d\x5f\x30\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("environment_specular_contribution_m_0 not found!")
                    try: 
                        Albedo_Specular_Tint_Blend_M_0_Offset = shaderfile_read.index(b'\x00\x61\x6c\x62\x65\x64\x6f\x5f\x73\x70\x65\x63\x75\x6c\x61\x72\x5f\x74\x69\x6e\x74\x5f\x62\x6c\x65\x6e\x64\x5f\x6d\x5f\x30\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("albedo_specular_tint_blend_m_0 not found!")
                    try: 
                        Diffuse_Coefficient_M_1_Offset = shaderfile_read.index(b'\x00\x64\x69\x66\x66\x75\x73\x65\x5F\x63\x6F\x65\x66\x66\x69\x63\x69\x65\x6E\x74\x5F\x6D\x5F\x31\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("diffuse_coefficient_m_1 not found!")
                    try: 
                        Specular_Coefficient_M_1_Offset = shaderfile_read.index(b'\x00\x73\x70\x65\x63\x75\x6C\x61\x72\x5F\x63\x6F\x65\x66\x66\x69\x63\x69\x65\x6E\x74\x5F\x6D\x5F\x31\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("specular_coefficient_m_1 not found!")
                    try: 
                        Specular_Power_M_1_Offset = shaderfile_read.index(b'\x00\x73\x70\x65\x63\x75\x6C\x61\x72\x5F\x70\x6F\x77\x65\x72\x5F\x6D\x5F\x31\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("specular_power_m_1 not found!")
                    try: 
                        Specular_Tint_M_1_Offset = shaderfile_read.index(b'\x00\x73\x70\x65\x63\x75\x6C\x61\x72\x5F\x74\x69\x6E\x74\x5F\x6D\x5F\x31\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("specular_tint_m_1 not found!")
                    try: 
                        Fresnel_Curve_Steepness_M_1_Offset = shaderfile_read.index(b'\x00\x66\x72\x65\x73\x6e\x65\x6c\x5f\x63\x75\x72\x76\x65\x5f\x73\x74\x65\x65\x70\x6e\x65\x73\x73\x5f\x6d\x5f\x31\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("fresnel_curve_steepness_m_1 not found!")
                    try: 
                        Area_Specular_Contribution_M_1_Offset = shaderfile_read.index(b'\x00\x61\x72\x65\x61\x5F\x73\x70\x65\x63\x75\x6C\x61\x72\x5F\x63\x6F\x6E\x74\x72\x69\x62\x75\x74\x69\x6F\x6E\x5F\x6D\x5F\x31\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("area_specular_contribution_m_1 not found!")
                    try: 
                        Analytical_Specular_Contribution_M_1_Offset = shaderfile_read.index(b'\x00\x61\x6E\x61\x6C\x79\x74\x69\x63\x61\x6C\x5F\x73\x70\x65\x63\x75\x6C\x61\x72\x5F\x63\x6F\x6E\x74\x72\x69\x62\x75\x74\x69\x6F\x6E\x5F\x6D\x5F\x31\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("analytical_specular_contribution_m_1 not found!")
                    try: 
                        Environment_Specular_Contribution_M_1_Offset = shaderfile_read.index(b'\x00\x65\x6e\x76\x69\x72\x6f\x6e\x6d\x65\x6e\x74\x5f\x73\x70\x65\x63\x75\x6c\x61\x72\x5f\x63\x6f\x6e\x74\x72\x69\x62\x75\x74\x69\x6f\x6e\x5f\x6d\x5f\x31\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("environment_specular_contribution_m_1 not found!")
                    try: 
                        Albedo_Specular_Tint_Blend_M_1_Offset = shaderfile_read.index(b'\x00\x61\x6c\x62\x65\x64\x6f\x5f\x73\x70\x65\x63\x75\x6c\x61\x72\x5f\x74\x69\x6e\x74\x5f\x62\x6c\x65\x6e\x64\x5f\x6d\x5f\x31\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("albedo_specular_tint_blend_m_1 not found!")
                    try: 
                        Diffuse_Coefficient_M_2_Offset = shaderfile_read.index(b'\x00\x64\x69\x66\x66\x75\x73\x65\x5F\x63\x6F\x65\x66\x66\x69\x63\x69\x65\x6E\x74\x5F\x6D\x5F\x32\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("diffuse_coefficient_m_2 not found!")
                    try: 
                        Specular_Coefficient_M_2_Offset = shaderfile_read.index(b'\x00\x73\x70\x65\x63\x75\x6C\x61\x72\x5F\x63\x6F\x65\x66\x66\x69\x63\x69\x65\x6E\x74\x5F\x6D\x5F\x32\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("specular_coefficient_m_2 not found!")
                    try: 
                        Specular_Power_M_2_Offset = shaderfile_read.index(b'\x00\x73\x70\x65\x63\x75\x6C\x61\x72\x5F\x70\x6F\x77\x65\x72\x5F\x6D\x5F\x32\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("specular_power_m_2 not found!")
                    try: 
                        Specular_Tint_M_2_Offset = shaderfile_read.index(b'\x00\x73\x70\x65\x63\x75\x6C\x61\x72\x5F\x74\x69\x6E\x74\x5F\x6D\x5F\x32\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("specular_tint_m_2 not found!")
                    try: 
                        Fresnel_Curve_Steepness_M_2_Offset = shaderfile_read.index(b'\x00\x66\x72\x65\x73\x6e\x65\x6c\x5f\x63\x75\x72\x76\x65\x5f\x73\x74\x65\x65\x70\x6e\x65\x73\x73\x5f\x6d\x5f\x32\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("fresnel_curve_steepness_m_2 not found!")
                    try: 
                        Area_Specular_Contribution_M_2_Offset = shaderfile_read.index(b'\x00\x61\x72\x65\x61\x5F\x73\x70\x65\x63\x75\x6C\x61\x72\x5F\x63\x6F\x6E\x74\x72\x69\x62\x75\x74\x69\x6F\x6E\x5F\x6D\x5F\x32\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("area_specular_contribution_m_2 not found!")
                    try: 
                        Analytical_Specular_Contribution_M_2_Offset = shaderfile_read.index(b'\x00\x61\x6E\x61\x6C\x79\x74\x69\x63\x61\x6C\x5F\x73\x70\x65\x63\x75\x6C\x61\x72\x5F\x63\x6F\x6E\x74\x72\x69\x62\x75\x74\x69\x6F\x6E\x5F\x6D\x5F\x32\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("analytical_specular_contribution_m_2 not found!")
                    try: 
                        Environment_Specular_Contribution_M_2_Offset = shaderfile_read.index(b'\x00\x65\x6e\x76\x69\x72\x6f\x6e\x6d\x65\x6e\x74\x5f\x73\x70\x65\x63\x75\x6c\x61\x72\x5f\x63\x6f\x6e\x74\x72\x69\x62\x75\x74\x69\x6f\x6e\x5f\x6d\x5f\x32\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("environment_specular_contribution_m_2 not found!")
                    try: 
                        Albedo_Specular_Tint_Blend_M_2_Offset = shaderfile_read.index(b'\x00\x61\x6c\x62\x65\x64\x6f\x5f\x73\x70\x65\x63\x75\x6c\x61\x72\x5f\x74\x69\x6e\x74\x5f\x62\x6c\x65\x6e\x64\x5f\x6d\x5f\x32\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("albedo_specular_tint_blend_m_2 not found!")
                    try: 
                        Diffuse_Coefficient_M_3_Offset = shaderfile_read.index(b'\x00\x64\x69\x66\x66\x75\x73\x65\x5F\x63\x6F\x65\x66\x66\x69\x63\x69\x65\x6E\x74\x5F\x6D\x5F\x33\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("diffuse_coefficient_m_3 not found!")
                    try: 
                        Specular_Coefficient_M_3_Offset = shaderfile_read.index(b'\x00\x73\x70\x65\x63\x75\x6C\x61\x72\x5F\x63\x6F\x65\x66\x66\x69\x63\x69\x65\x6E\x74\x5F\x6D\x5F\x33\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("specular_coefficient_m_3 not found!")
                    try: 
                        Specular_Power_M_3_Offset = shaderfile_read.index(b'\x00\x73\x70\x65\x63\x75\x6C\x61\x72\x5F\x70\x6F\x77\x65\x72\x5F\x6D\x5F\x33\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("specular_power_m_3 not found!")
                    try: 
                        Specular_Tint_M_3_Offset = shaderfile_read.index(b'\x00\x73\x70\x65\x63\x75\x6C\x61\x72\x5F\x74\x69\x6E\x74\x5F\x6D\x5F\x33\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("specular_tint_m_3 not found!")
                    try: 
                        Fresnel_Curve_Steepness_M_3_Offset = shaderfile_read.index(b'\x00\x66\x72\x65\x73\x6e\x65\x6c\x5f\x63\x75\x72\x76\x65\x5f\x73\x74\x65\x65\x70\x6e\x65\x73\x73\x5f\x6d\x5f\x33\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("fresnel_curve_steepness_m_3 not found!")
                    try: 
                        Area_Specular_Contribution_M_3_Offset = shaderfile_read.index(b'\x00\x61\x72\x65\x61\x5F\x73\x70\x65\x63\x75\x6C\x61\x72\x5F\x63\x6F\x6E\x74\x72\x69\x62\x75\x74\x69\x6F\x6E\x5F\x6D\x5F\x33\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("area_specular_contribution_m_3 not found!")
                    try: 
                        Analytical_Specular_Contribution_M_3_Offset = shaderfile_read.index(b'\x00\x61\x6E\x61\x6C\x79\x74\x69\x63\x61\x6C\x5F\x73\x70\x65\x63\x75\x6C\x61\x72\x5F\x63\x6F\x6E\x74\x72\x69\x62\x75\x74\x69\x6F\x6E\x5F\x6D\x5F\x33\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("analytical_specular_contribution_m_3 not found!")
                    try: 
                        Environment_Specular_Contribution_M_3_Offset = shaderfile_read.index(b'\x00\x65\x6e\x76\x69\x72\x6f\x6e\x6d\x65\x6e\x74\x5f\x73\x70\x65\x63\x75\x6c\x61\x72\x5f\x63\x6f\x6e\x74\x72\x69\x62\x75\x74\x69\x6f\x6e\x5f\x6d\x5f\x33\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("environment_specular_contribution_m_3 not found!")
                    try: 
                        Albedo_Specular_Tint_Blend_M_3_Offset = shaderfile_read.index(b'\x00\x61\x6c\x62\x65\x64\x6f\x5f\x73\x70\x65\x63\x75\x6c\x61\x72\x5f\x74\x69\x6e\x74\x5f\x62\x6c\x65\x6e\x64\x5f\x6d\x5f\x33\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            print("albedo_specular_tint_blend_m_3 not found!")                
                


      
                                        #################
                                        #CATEGORY OPTIONS
                                        #################
                
                ########
                #SHADERS
                ########             
                
                #if Shader file is .shader
                if (Shader_Type == 0):
                    #store category options for the material
                    print("")
                    print("--[Category Options]--")
                    if (CategoryOptions_Offset != 0):
                            shaderfile.seek(CategoryOptions_Offset + 0x22) #skips to start of Category options
                            ShaderItem.albedo_option = int.from_bytes(shaderfile.read(2), 'little')
                            ShaderItem.bump_mapping_option = int.from_bytes(shaderfile.read(2), 'little')
                            ShaderItem.alpha_test_option = int.from_bytes(shaderfile.read(2), 'little')
                            ShaderItem.specular_mask_option = int.from_bytes(shaderfile.read(2), 'little')
                            ShaderItem.material_model_option = int.from_bytes(shaderfile.read(2), 'little')
                            ShaderItem.environment_mapping_option = int.from_bytes(shaderfile.read(2), 'little')
                            ShaderItem.self_illumination_option = int.from_bytes(shaderfile.read(2), 'little')
                            ShaderItem.blend_mode_option = int.from_bytes(shaderfile.read(2), 'little')
                            ShaderItem.parallax_option = int.from_bytes(shaderfile.read(2), 'little')
                            ShaderItem.misc_option = int.from_bytes(shaderfile.read(2), 'little')
                            
                            print("albedo option: " + get_albedo_option(ShaderItem.albedo_option))
                            print("bump_mapping option: " + get_bump_mapping_option(ShaderItem.bump_mapping_option))
                            print("alpha_test option: " + get_alpha_test_option(ShaderItem.alpha_test_option))
                            print("specular_mask option: " + get_specular_mask_option(ShaderItem.specular_mask_option))
                            print("material_model option: " + get_material_model_option(ShaderItem.material_model_option))
                            print("environment_mapping option: " + get_environment_map_option(ShaderItem.environment_mapping_option))
                            print("self_illumination option: " + get_self_illumination_option(ShaderItem.self_illumination_option))
                            print("blend_mode option: " + get_blend_mode_option(ShaderItem.blend_mode_option))
                            print("parallax option: " + get_parallax_option(ShaderItem.parallax_option))
                            print("misc option: " + get_misc_option(ShaderItem.misc_option))


                ################
                #TERRAIN SHADERS
                ################

                #if Shader file is .shader_terrain
                elif (Shader_Type == 1):
                    #store category options for the material
                    print("")
                    print("--[Category Options]--")
                    if (CategoryOptions_Offset != 0):
                            shaderfile.seek(CategoryOptions_Offset + 0x28) #skips to start of Category options
                            ShaderItem.blending_option = int.from_bytes(shaderfile.read(2), 'little')
                            ShaderItem.environment_map_option = int.from_bytes(shaderfile.read(2), 'little')
                            ShaderItem.material_0_option = int.from_bytes(shaderfile.read(2), 'little')
                            ShaderItem.material_1_option = int.from_bytes(shaderfile.read(2), 'little')
                            ShaderItem.material_2_option = int.from_bytes(shaderfile.read(2), 'little')
                            ShaderItem.material_3_option = int.from_bytes(shaderfile.read(2), 'little')
                            
                            print("blending option: " + get_blending_option(ShaderItem.blending_option))
                            print("environment_map option: " + get_environment_map_terr_option(ShaderItem.environment_map_option))
                            print("material_0 option: " + get_material_0_option(ShaderItem.material_0_option))
                            print("material_1 option: " + get_material_1_option(ShaderItem.material_1_option))
                            print("material_2 option: " + get_material_2_option(ShaderItem.material_2_option))
                            print("material_3 option: " + get_material_3_option(ShaderItem.material_3_option))


                ################
                #FOLIAGE SHADERS
                ################
                #if Shader file is .shader_terrain
                elif (Shader_Type == 2):
                    #store category options for the material
                    print("")
                    print("--[Category Options]--")
                    if (CategoryOptions_Offset != 0):
                            shaderfile.seek(CategoryOptions_Offset + 0x23) #skips to start of Category options
                            ShaderItem.albedo_option = int.from_bytes(shaderfile.read(2), 'little')                       
                            ShaderItem.alpha_test_option = int.from_bytes(shaderfile.read(2), 'little')
                            ShaderItem.material_model_option = int.from_bytes(shaderfile.read(2), 'little')
                            
                            print("albedo option: " + get_albedo_foliage_option(ShaderItem.albedo_option))
                            print("alpha_test option: " + get_alpha_foliage_option(ShaderItem.alpha_test_option))
                            print("material_model option: " + get_material_foliage_option(ShaderItem.material_model_option))

                #################
                #HALOGRAM SHADERS
                #################
                if (Shader_Type == 3):
                    #store category options for the material
                    print("")
                    print("--[Category Options]--")
                    if (CategoryOptions_Offset != 0):
                            shaderfile.seek(CategoryOptions_Offset + 0x24) #skips to start of Category options
                            ShaderItem.albedo_option = int.from_bytes(shaderfile.read(2), 'little')
                            ShaderItem.self_illumination_option = int.from_bytes(shaderfile.read(2), 'little')   
                            ShaderItem.blend_mode_option = int.from_bytes(shaderfile.read(2), 'little')    
                            ShaderItem.misc_option = int.from_bytes(shaderfile.read(2), 'little')
                            ShaderItem.warp_option = int.from_bytes(shaderfile.read(2), 'little')
                            ShaderItem.overlay_option = int.from_bytes(shaderfile.read(2), 'little')
                            ShaderItem.edge_fade_option = int.from_bytes(shaderfile.read(2), 'little')
                            ShaderItem.distortion_option = int.from_bytes(shaderfile.read(2), 'little')
                            ShaderItem.soft_fade_option = int.from_bytes(shaderfile.read(2), 'little')

                            
                            print("albedo option: " + get_albedo_option(ShaderItem.albedo_option))
                            print("self_illumination option: " + get_halogram_self_illumination_option(ShaderItem.self_illumination))
                            print("blend_mode option: " + get_blend_mode_option(ShaderItem.blend_mode_option))                        
                            print("misc option: " + get_misc_option(ShaderItem.misc_option))                        
                            
                            print("warp_option option: " + get_warp_option(ShaderItem.warp_option))
                            print("overlay_option option: " + get_overlay_option(ShaderItem.overlay_option))
                            print("edge_fade_option option: " + get_edge_fade_option(ShaderItem.edge_fade_option))
                            print("distortion_option option: " + get_distortion_option(ShaderItem.distortion_option))
                            print("soft_fade_option option: " + get_soft_fade_option(ShaderItem.soft_fade_option))



                #Gather needed texture list
                ShaderItem = build_texture_list(ShaderItem, Shader_Type)

                                        #############
                                        #TEXTURE DATA
                                        #############
                                        
                ########
                # .SHADER FILES
                ########
                
                print("")
                print("--[Existing Texture Types]--")
                if (BaseMap_Offset != 0):
                    #print("base_map offset: " + str(BaseMap_Offset))
                    print("")
                    print("[base_map]")
                    #DirOffset = shaderfile.tell()
                    
                    #clear old bitmap data
                    Bitmap = bitmap()
                    Bitmap.directory = ""
                    Bitmap.type = ""
                    Bitmap.curve_option = 0
                    Bitmap.width = 0
                    Bitmap.height = 0
                    
                    #save current data
                    Bitmap.directory = get_dir(shaderfile, BaseMap_Offset + 0x18 + 0x1) 
                    print("Dir: " + Bitmap.directory)
                    Bitmap.type = "base_map"
                    if (Bitmap.directory == "" or Bitmap.directory == " " or Bitmap.directory == "   "):
                         DefaultNeeded = 1                 

                    if(DefaultNeeded != 1):
                        try:
                            #get Curve for bitmap
                            Bitmap.curve_option = get_bitmap_curve(Tag_Root + Bitmap.directory + ".bitmap")
                            
                            #Get Resolution of bitmap
                            Bitmap.width = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "width")
                            Bitmap.height = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "height")
                        except ValueError:
                            print("Bitmap Directory not referenced. Please use Default Data")
                    
                    #get scaling data for bitmap
                    Bitmap = get_scale(shaderfile, (BaseMap_Offset + 0x18 + 0x1), len(Bitmap.directory), Bitmap) #uniform scaling 
                        
                    ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                    ShaderItem.bitmap_list.append(Bitmap)
                    DefaultNeeded = 0
                else:
                    #bitmap not referenced but might be needed
                    if(is_texture_needed(ShaderItem, "base_map")):
                        print("")
                        print("[base_map]")
                        #DirOffset = shaderfile.tell()
                        
                        #clear old bitmap data
                        Bitmap = bitmap()
                        Bitmap.directory = ""
                        Bitmap.type = ""
                        Bitmap.curve_option = 0
                        Bitmap.width = 0
                        Bitmap.height = 0
                        
                        Bitmap.type = "base_map"
                        Bitmap.directory = correct_default_dir("base_map")
                        ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                        ShaderItem.bitmap_list.append(Bitmap)
                        
                if (DetailMap_Offset != 0):
                    #print("detail_map offset: " + str(DetailMap_Offset))
                    print("")
                    print("[detail_map]")
                    shaderfile.seek(DetailMap_Offset + 0x1A + 0x1)
                    
                    #clear old bitmap data
                    Bitmap = bitmap()
                    Bitmap.directory = ""
                    Bitmap.type = ""
                    Bitmap.curve_option = 0
                    Bitmap.width = 0
                    Bitmap.height = 0
                    
                    #save current data
                    Bitmap.directory = get_dir(shaderfile, DetailMap_Offset + 0x1A + 0x1)
                    print("Dir: " + Bitmap.directory)
                    Bitmap.type = "detail_map"
                    ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                    ShaderItem.bitmap_list.append(Bitmap)
                    if (Bitmap.directory == "" or Bitmap.directory == " " or Bitmap.directory == "   "):
                         DefaultNeeded = 1                 

                    
                    #try to correct directory empty issue from default values
                    if (Bitmap.directory == "" or Bitmap.directory == " " or Bitmap.directory == "  "):
                        #replace Bitmap.directory with default .bitmap directory
                        if(uses_gray_50(Bitmap.type) == True):
                            Bitmap.directory = "shaders/default_bitmaps/bitmaps/gray_50_percent"
                        elif(uses_color_white(Bitmap.type) == True):
                            Bitmap.directory = "shaders/default_bitmaps/bitmaps/color_white"
                        elif(uses_default_vector(Bitmap.type) == True):
                            Bitmap.directory = "shaders/default_bitmaps/bitmaps/default_vector"
                        elif(uses_reference_grids(Bitmap.type) == True):    
                            Bitmap.directory = "shaders/default_bitmaps/bitmaps/reference_grids"
                        elif(uses_default_alpha_test(Bitmap.type) == True):    
                            Bitmap.directory = "shaders/default_bitmaps/bitmaps/default_alpha_test"
                        elif(uses_default_dynamic_cube_map(Bitmap.type) == True):    
                            Bitmap.directory =  "shaders/default_bitmaps/bitmaps/default_dynamic_cube_map"
                        elif(uses_color_red(Bitmap.type) == True):    
                            Bitmap.directory = "shaders/default_bitmaps/bitmaps/color_red"
                        elif(uses_monochrome_alpha_grid(Bitmap.type) == True):    
                            Bitmap.directory = "shaders/default_bitmaps/bitmaps/monochrome_alpha_grid"
                        else:
                            Bitmap.directory = "shaders/default_bitmaps/bitmaps/default_detail"
                



                #if((Bitmap.type != "detail_map" and ShaderItem.detail_map_option != 0 ):
                    if (DefaultNeeded != 1):
                        try:
                            #get Curve for bitmap
                            Bitmap.curve_option = get_bitmap_curve(Tag_Root + Bitmap.directory + ".bitmap")
                            
                            #Get Resolution of bitmap
                            Bitmap.width = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "width")
                            Bitmap.height = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "height")
                        except ValueError:
                            print("Bitmap Directory not referenced. Please use Default Data")

                    #get scaling data for bitmap
                    Bitmap = get_scale(shaderfile, (DetailMap_Offset + 0x1A + 0x1), len(Bitmap.directory), Bitmap) #uniform scaling 

                    DefaultNeeded = 0
                
                else:
                    #bitmap not referenced but might be needed
                    if(is_texture_needed(ShaderItem, "detail_map")):
                        print("")
                        print("[detail_map]")
                        #DirOffset = shaderfile.tell()
                        
                        #clear old bitmap data
                        Bitmap = bitmap()
                        Bitmap.directory = ""
                        Bitmap.type = ""
                        Bitmap.curve_option = 0
                        Bitmap.width = 0
                        Bitmap.height = 0
                        
                        Bitmap.type = "detail_map"
                        Bitmap.directory = correct_default_dir("detail_map")
                        ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                        ShaderItem.bitmap_list.append(Bitmap)
                
                if (DetailMap2_Offset != 0):
                    #print("detail_map2 offset: " + str(DetailMap2_Offset)) 
                    print("")                
                    print("[detail_map2]")                
                    #shaderfile.seek(DetailMap2_Offset + 0x1B)
                    
                    #clear old bitmap data
                    Bitmap = bitmap()
                    Bitmap.directory = ""
                    Bitmap.type = ""
                    Bitmap.curve_option = 0
                    Bitmap.width = 0
                    Bitmap.height = 0
                    
                    #save current data
                    Bitmap.directory = get_dir(shaderfile, DetailMap2_Offset + 0x1B + 0x1)
                    print("Dir: " + Bitmap.directory)
                    Bitmap.type = "detail_map2"
                    ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                    ShaderItem.bitmap_list.append(Bitmap)
                    if (Bitmap.directory == "" or Bitmap.directory == " " or Bitmap.directory == "   "):
                         DefaultNeeded = 1                 

                    if (DefaultNeeded != 1):
                        try:
                            #get Curve for bitmap
                            Bitmap.curve_option = get_bitmap_curve(Tag_Root + Bitmap.directory + ".bitmap")
                            
                            #Get Resolution of bitmap
                            Bitmap.width = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "width")
                            Bitmap.height = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "height")
                        except OSError:
                            print("Bitmap Directory not referenced. Please use Default Data")
                   
                    Bitmap = get_scale(shaderfile, (DetailMap2_Offset + 0x1B + 0x1), len(Bitmap.directory), Bitmap) #uniform scaling 

                    DefaultNeeded = 0
                else:
                    #bitmap not referenced but might be needed
                    if(is_texture_needed(ShaderItem, "detail_map2")):
                        print("")
                        print("[detail_map2]")
                        #DirOffset = shaderfile.tell()
                        
                        #clear old bitmap data
                        Bitmap = bitmap()
                        Bitmap.directory = ""
                        Bitmap.type = ""
                        Bitmap.curve_option = 0
                        Bitmap.width = 0
                        Bitmap.height = 0
                        
                        Bitmap.type = "detail_map2"
                        Bitmap.directory = correct_default_dir("detail_map2")
                        ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                        ShaderItem.bitmap_list.append(Bitmap)
                
                
                #print("detail_map_overlay offset: " + str())
                if (DetailMap3_Offset != 0):
                    #print("detail_map3 offset: " + str(DetailMap3_Offset))
                    print("")
                    print("[detail_map3]") 
                    shaderfile.seek(DetailMap3_Offset + 0x1B + 0x1)
                    
                    #clear old bitmap data
                    Bitmap = bitmap()
                    Bitmap.directory = ""
                    Bitmap.type = ""
                    Bitmap.curve_option = 0
                    Bitmap.width = 0
                    Bitmap.height = 0
                    
                    #save current data
                    Bitmap.directory = get_dir(shaderfile, DetailMap3_Offset + 0x1B + 0x1)
                    print("Dir: " + Bitmap.directory)
                    Bitmap.type = "detail_map3"
                    ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                    ShaderItem.bitmap_list.append(Bitmap)
                    if (Bitmap.directory == "" or Bitmap.directory == " " or Bitmap.directory == "   "):
                         DefaultNeeded = 1 
                         
                    if (DefaultNeeded != 1):
                        try:
                            #get Curve for bitmap
                            Bitmap.curve_option = get_bitmap_curve(Tag_Root + Bitmap.directory + ".bitmap")
                            
                            #Get Resolution of bitmap
                            Bitmap.width = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "width")
                            Bitmap.height = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "height")
                        except ValueError:
                            print("Bitmap Directory not referenced. Please use Default Data")
                   
                    Bitmap = get_scale(shaderfile, (DetailMap3_Offset + 0x1B + 0x1), len(Bitmap.directory), Bitmap) #uniform scaling 

                    DefaultNeeded = 0
                else:
                    #bitmap not referenced but might be needed
                    if(is_texture_needed(ShaderItem, "detail_map3")):
                        print("")
                        print("[detail_map3]")
                        #DirOffset = shaderfile.tell()
                        
                        #clear old bitmap data
                        Bitmap = bitmap()
                        Bitmap.directory = ""
                        Bitmap.type = ""
                        Bitmap.curve_option = 0
                        Bitmap.width = 0
                        Bitmap.height = 0
                        
                        Bitmap.type = "detail_map3"
                        Bitmap.directory = correct_default_dir("detail_map3")
                        ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                        ShaderItem.bitmap_list.append(Bitmap)

                if (SpecularMaskTexture_Offset != 0):
                    #print("specular_mask_texture offset: " + str(SpecularMaskTexture_Offset))
                    print("")
                    print("[specular_mask_texture]") 
                    shaderfile.seek(SpecularMaskTexture_Offset + 0x25 + 0x1)
                    
                    #clear old bitmap data
                    Bitmap = bitmap()
                    Bitmap.directory = ""
                    Bitmap.type = ""
                    Bitmap.curve_option = 0
                    Bitmap.width = 0
                    Bitmap.height = 0
                    
                    #save current data
                    Bitmap.directory = get_dir(shaderfile, SpecularMaskTexture_Offset + 0x25 + 0x1)
                    print("Dir: " + Bitmap.directory)
                    Bitmap.type = "specular_mask_texture"
                    ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                    ShaderItem.bitmap_list.append(Bitmap)
                    if (Bitmap.directory == "" or Bitmap.directory == " " or Bitmap.directory == "   "):
                         DefaultNeeded = 1 

                    if (DefaultNeeded != 1):
                        try:
                            #get Curve for bitmap
                            Bitmap.curve_option = get_bitmap_curve(Tag_Root + Bitmap.directory + ".bitmap")
                            
                            #Get Resolution of bitmap
                            Bitmap.width = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "width")
                            Bitmap.height = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "height")
                        except OSError:
                            print("Bitmap Directory not referenced. Please use Default Data")
                   
                    Bitmap = get_scale(shaderfile, (SpecularMaskTexture_Offset + 0x25 + 0x1), len(Bitmap.directory), Bitmap) #uniform scaling 

                    DefaultNeeded = 0
                else:
                    #bitmap not referenced but might be needed
                    if(is_texture_needed(ShaderItem, "specular_mask_texture")):
                        print("")
                        print("[specular_mask_texture]")
                        #DirOffset = shaderfile.tell()
                        
                        #clear old bitmap data
                        Bitmap = bitmap()
                        Bitmap.directory = ""
                        Bitmap.type = ""
                        Bitmap.curve_option = 0
                        Bitmap.width = 0
                        Bitmap.height = 0
                        
                        Bitmap.type = "specular_mask_texture"
                        Bitmap.directory = correct_default_dir("specular_mask_texture")
                        ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                        ShaderItem.bitmap_list.append(Bitmap)
    
                if (ChangeColorMap_Offset != 0):
                    #print("change_color_map offset: " + str(ChangeColorMap_Offset))
                    print("")
                    print("[change_color_map]") 
                    shaderfile.seek(ChangeColorMap_Offset + 0x20 + 0x1)
                    
                    #clear old bitmap data
                    Bitmap = bitmap()
                    Bitmap.directory = ""
                    Bitmap.type = ""
                    Bitmap.curve_option = 0
                    Bitmap.width = 0
                    Bitmap.height = 0
                    
                    #save current data
                    Bitmap.directory = get_dir(shaderfile, ChangeColorMap_Offset + 0x20 + 0x1)
                    print("Dir: " + Bitmap.directory)
                    Bitmap.type = "change_color_map"
                    ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                    ShaderItem.bitmap_list.append(Bitmap)
                    if (Bitmap.directory == "" or Bitmap.directory == " " or Bitmap.directory == "   "):
                         DefaultNeeded = 1 

                    if (DefaultNeeded != 1):
                        try:
                            #get Curve for bitmap
                            Bitmap.curve_option = get_bitmap_curve(Tag_Root + Bitmap.directory + ".bitmap")
                            
                            #Get Resolution of bitmap
                            Bitmap.width = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "width")
                            Bitmap.height = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "height")
                        except OSError:
                            print("Bitmap Directory not referenced. Please use Default Data")
                   
                    Bitmap = get_scale(shaderfile, (ChangeColorMap_Offset + 0x20 + 0x1), len(Bitmap.directory), Bitmap) #uniform scaling 

                    DefaultNeeded = 0
                else:
                    #bitmap not referenced but might be needed
                    if(is_texture_needed(ShaderItem, "change_color_map")):
                        print("")
                        print("[change_color_map]")
                        #DirOffset = shaderfile.tell()
                        
                        #clear old bitmap data
                        Bitmap = bitmap()
                        Bitmap.directory = ""
                        Bitmap.type = ""
                        Bitmap.curve_option = 0
                        Bitmap.width = 0
                        Bitmap.height = 0
                        
                        Bitmap.type = "change_color_map"
                        Bitmap.directory = correct_default_dir("change_color_map")
                        ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                        ShaderItem.bitmap_list.append(Bitmap)

                if (BumpMap_Offset != 0):
                    #print("bump_map offset: " + str(BumpMap_Offset))
                    print("")
                    print("[bump_map]") 
                    shaderfile.seek(BumpMap_Offset + 0x18 + 0x1)
                    
                    #clear old bitmap data
                    Bitmap = bitmap()
                    Bitmap.directory = ""
                    Bitmap.type = ""
                    Bitmap.curve_option = 0
                    Bitmap.width = 0
                    Bitmap.height = 0
                    
                    #save current data
                    Bitmap.directory = get_dir(shaderfile, BumpMap_Offset + 0x18 + 0x1)
                    print("Dir: " + Bitmap.directory)
                    Bitmap.type = "bump_map"
                    ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                    ShaderItem.bitmap_list.append(Bitmap)
                    if (Bitmap.directory == "" or Bitmap.directory == " " or Bitmap.directory == "   "):
                         DefaultNeeded = 1                 
                    
                    #print("bump mapping option: " + str(ShaderItem.bump_mapping_option))
                    if not (ShaderItem.bump_mapping_option == 0):
                        if (DefaultNeeded != 1):
                            try:
                                #get Curve for bitmap
                                Bitmap.curve_option = get_bitmap_curve(Tag_Root + Bitmap.directory + ".bitmap")
                                
                                #Get Resolution of bitmap
                                Bitmap.width = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "width")
                                Bitmap.height = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "height")
                            except OSError:
                                print("Bitmap Directory not referenced. Please use Default Data")
                    

                    Bitmap = get_scale(shaderfile, (BumpMap_Offset + 0x18 + 0x1), len(Bitmap.directory), Bitmap) #uniform scaling 

                    DefaultNeeded = 0
                else:
                    #bitmap not referenced but might be needed
                    if(is_texture_needed(ShaderItem, "bump_map")):
                        print("")
                        print("[bump_map]")
                        #DirOffset = shaderfile.tell()
                        
                        #clear old bitmap data
                        Bitmap = bitmap()
                        Bitmap.directory = ""
                        Bitmap.type = ""
                        Bitmap.curve_option = 0
                        Bitmap.width = 0
                        Bitmap.height = 0
                        
                        Bitmap.type = "bump_map"
                        Bitmap.directory = correct_default_dir("bump_map")
                        ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                        ShaderItem.bitmap_list.append(Bitmap)

                if (BumpDetailMap_Offset != 0):
                    #print("bump_detail_map offset: " + str(BumpDetailMap_Offset))
                    print("")
                    print("[bump_detail_map]")                
                    shaderfile.seek(BumpDetailMap_Offset + 0x1F + 0x1)
                    
                    #clear old bitmap data
                    Bitmap = bitmap()
                    Bitmap.directory = ""
                    Bitmap.type = ""
                    Bitmap.curve_option = 0
                    Bitmap.width = 0
                    Bitmap.height = 0
                    
                    #save current data
                    Bitmap.directory = get_dir(shaderfile, BumpDetailMap_Offset + 0x1F + 0x1)
                    print("Dir: " + Bitmap.directory)
                    Bitmap.type = "bump_detail_map"
                    ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                    ShaderItem.bitmap_list.append(Bitmap)
                    
                    if (Bitmap.directory == "" or Bitmap.directory == " " or Bitmap.directory == "   "):
                         DefaultNeeded = 1 
                    
                    #do this stuff if certain options aren't turned off
                    if (ShaderItem.environment_mapping_option != 1 and ShaderItem.environment_mapping_option != 0):
                        if (DefaultNeeded != 1):
                            try:
                                #get Curve for bitmap
                                Bitmap.curve_option = get_bitmap_curve(Tag_Root + Bitmap.directory + ".bitmap")
                                
                                #Get Resolution of bitmap
                                Bitmap.width = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "width")
                                Bitmap.height = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "height")
                            except OSError:
                                print("Bitmap Directory not referenced. Please use Default Data")
                        
                    Bitmap = get_scale(shaderfile, (BumpDetailMap_Offset + 0x1F + 0x1), len(Bitmap.directory), Bitmap) #uniform scaling 

                    DefaultNeeded = 0
                else:
                    #bitmap not referenced but might be needed
                    if(is_texture_needed(ShaderItem, "bump_detail_map")):
                        print("")
                        print("[bump_detail_map]")
                        #DirOffset = shaderfile.tell()
                        
                        #clear old bitmap data
                        Bitmap = bitmap()
                        Bitmap.directory = ""
                        Bitmap.type = ""
                        Bitmap.curve_option = 0
                        Bitmap.width = 0
                        Bitmap.height = 0
                        
                        Bitmap.type = "bump_detail_map"
                        Bitmap.directory = correct_default_dir("bump_detail_map")
                        ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                        ShaderItem.bitmap_list.append(Bitmap)

                if (EnvironmentMap_Offset != 0):
                    #print("environment_map offset: " + str(EnvironmentMap_Offset))
                    print("")
                    print("[environment_map]")                
                    shaderfile.seek(EnvironmentMap_Offset + 0x1F + 0x1)
                    
                    #clear old bitmap data
                    Bitmap = bitmap()
                    Bitmap.directory = ""
                    Bitmap.type = ""
                    Bitmap.curve_option = 0
                    Bitmap.width = 0
                    Bitmap.height = 0
                    
                    #save current data
                    Bitmap.directory = get_dir(shaderfile, EnvironmentMap_Offset + 0x1F + 0x1)
                    print("Dir: " + Bitmap.directory)
                    Bitmap.type = "environment_map"
                    ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                    ShaderItem.bitmap_list.append(Bitmap)
                    if (Bitmap.directory == "" or Bitmap.directory == " " or Bitmap.directory == "   "):
                         DefaultNeeded = 1 
                    
                    
                    if (ShaderItem.environment_mapping_option == 3):
                        
                        if (FlatEnvironmentMap_Offset != 0):
                            #print("environment_map offset: " + str(EnvironmentMap_Offset))
                            print("")
                            print("[flat_environment_map]")                
                            shaderfile.seek(FlatEnvironmentMap_Offset + 0x24 + 0x1)
                            
                            #clear old bitmap data
                            Bitmap = bitmap()
                            Bitmap.directory = ""
                            Bitmap.type = ""
                            Bitmap.curve_option = 0
                            Bitmap.width = 0
                            Bitmap.height = 0
                            
                            #save current data
                            Bitmap.directory = get_dir(shaderfile, FlatEnvironmentMap_Offset + 0x24 + 0x1)
                            print("Dir: " + Bitmap.directory)
                            Bitmap.type = "flat_environment_map"
                            ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                            ShaderItem.bitmap_list.append(Bitmap)
                            
                            #resets DefaultNeeded value due to it being in another layer starting over
                            DefaultNeeded = 0
                            
                            if (Bitmap.directory == "" or Bitmap.directory == " " or Bitmap.directory == "   "):
                                DefaultNeeded = 1 

                            if (ShaderItem.environment_mapping_option != 0):
                                if(DefaultNeeded != 1):
                                    try:
                                        #get Curve for bitmap
                                        Bitmap.curve_option = get_bitmap_curve(Tag_Root + Bitmap.directory + ".bitmap")
                                        
                                        #Get Resolution of bitmap
                                        Bitmap.width = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "width")
                                        Bitmap.height = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "height")
                                    except OSError:
                                        print("Bitmap Directory not referenced. Please use Default Data")
                               
                                Bitmap = get_scale(shaderfile, (FlatEnvironmentMap_Offset + 0x24 + 0x1), len(Bitmap.directory), Bitmap) #uniform scaling 

                        
                    elif (ShaderItem.environment_mapping_option != 0):
                        if (DefaultNeeded != 1):
                            try:
                                #get Curve for bitmap
                                Bitmap.curve_option = get_bitmap_curve(Tag_Root + Bitmap.directory + ".bitmap")
                                
                                #Get Resolution of bitmap
                                Bitmap.width = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "width")
                                Bitmap.height = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "height")
                            except OSError:
                                print("Bitmap Directory not referenced. Please use Default Data")
                        
                        #get scaling data for bitmap
                        Bitmap = get_scale(shaderfile, (EnvironmentMap_Offset + 0x1F + 0x1), len(Bitmap.directory), Bitmap) #uniform scaling 

                    DefaultNeeded = 0

                if (SelfIllumMap_Offset != 0):
                    #print("self_illum_map offset: " + str(SelfIllumMap_Offset))
                    print("")
                    print("[self_illum_map]") 
                    shaderfile.seek(SelfIllumMap_Offset + 0x1E + 0x1)
                    
                    #clear old bitmap data
                    Bitmap = bitmap()
                    Bitmap.directory = ""
                    Bitmap.type = ""
                    Bitmap.curve_option = 0
                    Bitmap.width = 0
                    Bitmap.height = 0
                    
                    #save current data
                    Bitmap.directory = get_dir(shaderfile, SelfIllumMap_Offset + 0x1E + 0x1)
                    print("Dir: " + Bitmap.directory)
                    Bitmap.type = "self_illum_map"
                    ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                    ShaderItem.bitmap_list.append(Bitmap)
                    if (Bitmap.directory == "" or Bitmap.directory == " " or Bitmap.directory == "   "):
                         DefaultNeeded = 1 
                
                    if (ShaderItem.self_illumination_option != 0):
                        if(DefaultNeeded != 1):
                            try:
                                #get Curve for bitmap
                                Bitmap.curve_option = get_bitmap_curve(Tag_Root + Bitmap.directory + ".bitmap")
                                
                                #Get Resolution of bitmap
                                Bitmap.width = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "width")
                                Bitmap.height = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "height")
                            except OSError:
                                print("Bitmap Directory not referenced. Please use Default Data")
                    
                    #get scaling data for bitmap
                    Bitmap = get_scale(shaderfile, (SelfIllumMap_Offset + 0x1E + 0x1), len(Bitmap.directory), Bitmap) #uniform scaling 

                    DefaultNeeded = 0
                else:
                    #bitmap not referenced but might be needed
                    if(is_texture_needed(ShaderItem, "self_illum_map")):
                        print("")
                        print("[self_illum_map]")
                        #DirOffset = shaderfile.tell()
                        
                        #clear old bitmap data
                        Bitmap = bitmap()
                        Bitmap.directory = ""
                        Bitmap.type = ""
                        Bitmap.curve_option = 0
                        Bitmap.width = 0
                        Bitmap.height = 0
                        
                        Bitmap.type = "self_illum_map"
                        Bitmap.directory = correct_default_dir("self_illum_map")
                        ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                        ShaderItem.bitmap_list.append(Bitmap)
                
                if (SelfIllumDetailMap_Offset != 0):
                    #print("self_illum_detail_map offset: " + str(SelfIllumDetailMap_Offset))
                    print("")
                    print("[self_illum_detail_map]")
                    shaderfile.seek(SelfIllumDetailMap_Offset + 0x25 + 0x1)
                    
                    #clear old bitmap data
                    Bitmap = bitmap()
                    Bitmap.directory = ""
                    Bitmap.type = ""
                    Bitmap.curve_option = 0
                    Bitmap.width = 0
                    Bitmap.height = 0
                    
                    #save current data
                    Bitmap.directory = get_dir(shaderfile, SelfIllumDetailMap_Offset + 0x25 + 0x1)
                    print("Dir: " + Bitmap.directory)
                    Bitmap.type = "self_illum_detail_map"
                    ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                    ShaderItem.bitmap_list.append(Bitmap)
                    if (Bitmap.directory == "" or Bitmap.directory == " " or Bitmap.directory == "   "):
                         DefaultNeeded = 1 
                    
                    if(DefaultNeeded != 1 and ShaderItem.self_illumination_option != 0 and  ShaderItem.self_illumination_option != 1):
                        try:
                            #get Curve for bitmap
                            Bitmap.curve_option = get_bitmap_curve(Tag_Root + Bitmap.directory + ".bitmap")
                            
                            #Get Resolution of bitmap
                            Bitmap.width = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "width")
                            Bitmap.height = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "height")
                        except OSError:
                            print("Bitmap Directory not referenced. Please use Default Data")
                    
                    #get scaling data for bitmap
                    Bitmap = get_scale(shaderfile, (SelfIllumDetailMap_Offset + 0x25 + 0x1), len(Bitmap.directory), Bitmap) #uniform scaling 

                    DefaultNeeded = 0
                else:
                    #bitmap not referenced but might be needed
                    if(is_texture_needed(ShaderItem, "self_illum_detail_map")):
                        print("")
                        print("[self_illum_detail_map]")
                        #DirOffset = shaderfile.tell()
                        
                        #clear old bitmap data
                        Bitmap = bitmap()
                        Bitmap.directory = ""
                        Bitmap.type = ""
                        Bitmap.curve_option = 0
                        Bitmap.width = 0
                        Bitmap.height = 0
                        
                        Bitmap.type = "self_illum_detail_map"
                        Bitmap.directory = correct_default_dir("self_illum_detail_map")
                        ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                        ShaderItem.bitmap_list.append(Bitmap)

                #ALPHA_TEST_MAP
                if (AlphaTestMap_Offset != 0):
                    #print("base_map offset: " + str(BaseMap_Offset))
                    print("")
                    print("[alpha_test_map]")
                    #DirOffset = shaderfile.tell()
                    
                    #clear old bitmap data
                    Bitmap = bitmap()
                    Bitmap.directory = ""
                    Bitmap.type = ""
                    Bitmap.curve_option = 0
                    Bitmap.width = 0
                    Bitmap.height = 0
                    
                    #save current data
                    Bitmap.directory = get_dir(shaderfile, AlphaTestMap_Offset + 0x1E + 0x1)
                    print("Dir: " + Bitmap.directory)
                    Bitmap.type = "alpha_test_map"
                    if (Bitmap.directory == "" or Bitmap.directory == " " or Bitmap.directory == "   "):
                         DefaultNeeded = 1                 

                    #store the alpha_test_map directory for later
                    if(DefaultNeeded != 1):
                        ShaderItem.alpha_bitmap_dir = Bitmap.directory

                    if(DefaultNeeded != 1):
                        try:
                            #get Curve for bitmap
                            Bitmap.curve_option = get_bitmap_curve(Tag_Root + Bitmap.directory + ".bitmap")
                            
                            #Get Resolution of bitmap
                            Bitmap.width = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "width")
                            Bitmap.height = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "height")
                        except OSError:
                            print("Bitmap Directory not referenced. Please use Default Data")
                    
                    #get scaling data for bitmap
                    Bitmap = get_scale(shaderfile, (AlphaTestMap_Offset + 0x1E + 0x1), len(Bitmap.directory), Bitmap) #uniform scaling 

                        
                    ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                    ShaderItem.bitmap_list.append(Bitmap)
                    
                    DefaultNeeded = 0

                
                
                #################
                #TERRAIN SHADERS
                #################
                
                #BLEND_MAP OFFSET
                if (Blend_Map_Offset != 0):
                    #print("self_illum_map offset: " + str(SelfIllumMap_Offset))
                    print("")
                    print("[blend_map]") 
                    shaderfile.seek(Blend_Map_Offset + 0x10 + 0x9 + 0x1)
                    
                    #clear old bitmap data
                    Bitmap = bitmap()
                    Bitmap.directory = ""
                    Bitmap.type = ""
                    Bitmap.curve_option = 0
                    Bitmap.width = 0
                    Bitmap.height = 0
                    
                    #save current data
                    Bitmap.directory = get_dir(shaderfile, Blend_Map_Offset + 0x10 + 0x9 + 0x1)
                    print("Dir: " + Bitmap.directory)
                    Bitmap.type = "blend_map"
                    ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                    ShaderItem.bitmap_list.append(Bitmap)
                    if (Bitmap.directory == "" or Bitmap.directory == " " or Bitmap.directory == "   "):
                         DefaultNeeded = 1 
                
                    if(DefaultNeeded != 1):
                        try:
                            #get Curve for bitmap
                            Bitmap.curve_option = get_bitmap_curve(Tag_Root + Bitmap.directory + ".bitmap")
                            
                            #Get Resolution of bitmap
                            Bitmap.width = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "width")
                            Bitmap.height = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "height")
                        except OSError:
                            print("Bitmap Directory not referenced. Please use Default Data")
                    
                    #get scaling data for bitmap
                    Bitmap = get_scale(shaderfile, (Blend_Map_Offset + 0x10 + 0x9 + 0x1), len(Bitmap.directory), Bitmap) #uniform scaling 

                    DefaultNeeded = 0
                else:
                    #bitmap not referenced but might be needed
                    if(is_texture_needed(ShaderItem, "blend_map")):
                        print("")
                        print("[blend_map]")
                        #DirOffset = shaderfile.tell()
                        
                        #clear old bitmap data
                        Bitmap = bitmap()
                        Bitmap.directory = ""
                        Bitmap.type = ""
                        Bitmap.curve_option = 0
                        Bitmap.width = 0
                        Bitmap.height = 0
                        
                        Bitmap.type = "blend_map"
                        Bitmap.directory = correct_default_dir("blend_map")
                        ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                        ShaderItem.bitmap_list.append(Bitmap)
                
                #BASE_MAP_M_0 OFFSET
                if (Base_Map_M_0_Offset != 0):
                    #print("self_illum_map offset: " + str(SelfIllumMap_Offset))
                    print("")
                    print("[base_map_m_0]") 
                    shaderfile.seek(Base_Map_M_0_Offset + 0x10 + 0xC + 0x1)
                    
                    #clear old bitmap data
                    Bitmap = bitmap()
                    Bitmap.directory = ""
                    Bitmap.type = ""
                    Bitmap.curve_option = 0
                    Bitmap.width = 0
                    Bitmap.height = 0
                    
                    #save current data
                    Bitmap.directory = get_dir(shaderfile, Base_Map_M_0_Offset + 0x10 + 0xC + 0x1)
                    print("Dir: " + Bitmap.directory)
                    Bitmap.type = "base_map_m_0"
                    ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                    ShaderItem.bitmap_list.append(Bitmap)
                    if (Bitmap.directory == "" or Bitmap.directory == " " or Bitmap.directory == "   "):
                         DefaultNeeded = 1 
                
                    if(DefaultNeeded != 1):
                        try:
                            #get Curve for bitmap
                            Bitmap.curve_option = get_bitmap_curve(Tag_Root + Bitmap.directory + ".bitmap")
                            
                            #Get Resolution of bitmap
                            Bitmap.width = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "width")
                            Bitmap.height = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "height")
                        except OSError:
                            print("Bitmap Directory not referenced. Please use Default Data")
                    
                    #get scaling data for bitmap
                    Bitmap = get_scale(shaderfile, (Base_Map_M_0_Offset + 0x10 + 0xC + 0x1), len(Bitmap.directory), Bitmap) #uniform scaling 

                    DefaultNeeded = 0            
                else:
                    #bitmap not referenced but might be needed
                    if(is_texture_needed(ShaderItem, "base_map_m_0")):
                        print("")
                        print("[base_map_m_0]")
                        #DirOffset = shaderfile.tell()
                        
                        #clear old bitmap data
                        Bitmap = bitmap()
                        Bitmap.directory = ""
                        Bitmap.type = ""
                        Bitmap.curve_option = 0
                        Bitmap.width = 0
                        Bitmap.height = 0
                        
                        Bitmap.type = "base_map_m_0"
                        Bitmap.directory = correct_default_dir("base_map_m_0")
                        ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                        ShaderItem.bitmap_list.append(Bitmap)
                
                #DETAIL_MAP_M_0 OFFSET
                if (Detail_Map_M_0_Offset != 0):
                    #print("self_illum_map offset: " + str(SelfIllumMap_Offset))
                    print("")
                    print("[detail_map_m_0]") 
                    shaderfile.seek(Detail_Map_M_0_Offset + 0x10 + 0xE + 0x1)
                    
                    #clear old bitmap data
                    Bitmap = bitmap()
                    Bitmap.directory = ""
                    Bitmap.type = ""
                    Bitmap.curve_option = 0
                    Bitmap.width = 0
                    Bitmap.height = 0
                    
                    #save current data
                    Bitmap.directory = get_dir(shaderfile, Detail_Map_M_0_Offset + 0x10 + 0xE + 0x1)
                    print("Dir: " + Bitmap.directory)
                    Bitmap.type = "detail_map_m_0"
                    ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                    ShaderItem.bitmap_list.append(Bitmap)
                    if (Bitmap.directory == "" or Bitmap.directory == " " or Bitmap.directory == "   "):
                         DefaultNeeded = 1 
                
                    if(DefaultNeeded != 1):
                        try:
                            #get Curve for bitmap
                            Bitmap.curve_option = get_bitmap_curve(Tag_Root + Bitmap.directory + ".bitmap")
                            
                            #Get Resolution of bitmap
                            Bitmap.width = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "width")
                            Bitmap.height = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "height")
                        except OSError:
                            print("Bitmap Directory not referenced. Please use Default Data")
                    
                    #get scaling data for bitmap
                    Bitmap = get_scale(shaderfile, (Detail_Map_M_0_Offset + 0x10 + 0xE + 0x1), len(Bitmap.directory), Bitmap) #uniform scaling 

                    DefaultNeeded = 0             
                else:
                    #bitmap not referenced but might be needed
                    if(is_texture_needed(ShaderItem, "detail_map_m_0")):
                        print("")
                        print("[detail_map_m_0]")
                        #DirOffset = shaderfile.tell()
                        
                        #clear old bitmap data
                        Bitmap = bitmap()
                        Bitmap.directory = ""
                        Bitmap.type = ""
                        Bitmap.curve_option = 0
                        Bitmap.width = 0
                        Bitmap.height = 0
                        
                        Bitmap.type = "detail_map_m_0"
                        Bitmap.directory = correct_default_dir("detail_map_m_0")
                        ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                        ShaderItem.bitmap_list.append(Bitmap)
                
                #BUMP_MAP_M_0 OFFSET
                if (Bump_Map_M_0_Offset != 0):
                    #print("self_illum_map offset: " + str(SelfIllumMap_Offset))
                    print("")
                    print("[bump_map_m_0]") 
                    shaderfile.seek(Bump_Map_M_0_Offset + 0x10 + 0xC + 0x1)
                    
                    #clear old bitmap data
                    Bitmap = bitmap()
                    Bitmap.directory = ""
                    Bitmap.type = ""
                    Bitmap.curve_option = 0
                    Bitmap.width = 0
                    Bitmap.height = 0
                    
                    #save current data
                    Bitmap.directory = get_dir(shaderfile, Bump_Map_M_0_Offset + 0x10 + 0xC + 0x1)
                    print("Dir: " + Bitmap.directory)
                    Bitmap.type = "bump_map_m_0"
                    ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                    ShaderItem.bitmap_list.append(Bitmap)
                    if (Bitmap.directory == "" or Bitmap.directory == " " or Bitmap.directory == "   "):
                         DefaultNeeded = 1 
                
                    if(DefaultNeeded != 1):
                        try:
                            #get Curve for bitmap
                            Bitmap.curve_option = get_bitmap_curve(Tag_Root + Bitmap.directory + ".bitmap")
                            
                            #Get Resolution of bitmap
                            Bitmap.width = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "width")
                            Bitmap.height = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "height")
                        except OSError:
                            print("Bitmap Directory not referenced. Please use Default Data")
                    
                    #get scaling data for bitmap
                    Bitmap = get_scale(shaderfile, (Bump_Map_M_0_Offset + 0x10 + 0xC + 0x1), len(Bitmap.directory), Bitmap) #uniform scaling 

                    DefaultNeeded = 0  
                else:
                    #bitmap not referenced but might be needed
                    if(is_texture_needed(ShaderItem, "bump_map_m_0")):
                        print("")
                        print("[bump_map_m_0]")
                        #DirOffset = shaderfile.tell()
                        
                        #clear old bitmap data
                        Bitmap = bitmap()
                        Bitmap.directory = ""
                        Bitmap.type = ""
                        Bitmap.curve_option = 0
                        Bitmap.width = 0
                        Bitmap.height = 0
                        
                        Bitmap.type = "bump_map_m_0"
                        Bitmap.directory = correct_default_dir("bump_map_m_0")
                        ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                        ShaderItem.bitmap_list.append(Bitmap)
                
                #Detail_Bump_M_0_Offset OFFSET
                if (Detail_Bump_M_0_Offset != 0):
                    #print("self_illum_map offset: " + str(SelfIllumMap_Offset))
                    print("")
                    print("[detail_bump_m_0]") 
                    shaderfile.seek(Detail_Bump_M_0_Offset + 0x10 + 0xF + 0x1)
                    
                    #clear old bitmap data
                    Bitmap = bitmap()
                    Bitmap.directory = ""
                    Bitmap.type = ""
                    Bitmap.curve_option = 0
                    Bitmap.width = 0
                    Bitmap.height = 0
                    
                    #save current data
                    Bitmap.directory = get_dir(shaderfile, Detail_Bump_M_0_Offset + 0x10 + 0xF + 0x1)
                    print("Dir: " + Bitmap.directory)
                    Bitmap.type = "detail_bump_m_0"
                    ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                    ShaderItem.bitmap_list.append(Bitmap)
                    if (Bitmap.directory == "" or Bitmap.directory == " " or Bitmap.directory == "   "):
                         DefaultNeeded = 1 
                
                    if(DefaultNeeded != 1):
                        try:
                            #get Curve for bitmap
                            Bitmap.curve_option = get_bitmap_curve(Tag_Root + Bitmap.directory + ".bitmap")
                            
                            #Get Resolution of bitmap
                            Bitmap.width = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "width")
                            Bitmap.height = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "height")
                        except OSError:
                            print("Bitmap Directory not referenced. Please use Default Data")
                    
                    #get scaling data for bitmap
                    Bitmap = get_scale(shaderfile, (Detail_Bump_M_0_Offset + 0x10 + 0xF + 0x1), len(Bitmap.directory), Bitmap) #uniform scaling 

                    DefaultNeeded = 0 
                else:
                    #bitmap not referenced but might be needed
                    if(is_texture_needed(ShaderItem, "detail_bump_m_0")):
                        print("")
                        print("[detail_bump_m_0]")
                        #DirOffset = shaderfile.tell()
                        
                        #clear old bitmap data
                        Bitmap = bitmap()
                        Bitmap.directory = ""
                        Bitmap.type = ""
                        Bitmap.curve_option = 0
                        Bitmap.width = 0
                        Bitmap.height = 0
                        
                        Bitmap.type = "detail_bump_m_0"
                        Bitmap.directory = correct_default_dir("detail_bump_m_0")
                        ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                        ShaderItem.bitmap_list.append(Bitmap)

                #BASE_MAP_M_1 OFFSET
                if (Base_Map_M_1_Offset != 0):
                    #print("self_illum_map offset: " + str(SelfIllumMap_Offset))
                    print("")
                    print("[base_map_m_1]") 
                    shaderfile.seek(Base_Map_M_1_Offset + 0x10 + 0xC + 0x1)
                    
                    #clear old bitmap data
                    Bitmap = bitmap()
                    Bitmap.directory = ""
                    Bitmap.type = ""
                    Bitmap.curve_option = 0
                    Bitmap.width = 0
                    Bitmap.height = 0
                    
                    #save current data
                    Bitmap.directory = get_dir(shaderfile, Base_Map_M_1_Offset + 0x10 + 0xC + 0x1)
                    print("Dir: " + Bitmap.directory)
                    Bitmap.type = "base_map_m_1"
                    ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                    ShaderItem.bitmap_list.append(Bitmap)
                    if (Bitmap.directory == "" or Bitmap.directory == " " or Bitmap.directory == "   "):
                         DefaultNeeded = 1 
                
                    if(DefaultNeeded != 1):
                        try:
                            #get Curve for bitmap
                            Bitmap.curve_option = get_bitmap_curve(Tag_Root + Bitmap.directory + ".bitmap")
                            
                            #Get Resolution of bitmap
                            Bitmap.width = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "width")
                            Bitmap.height = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "height")
                        except OSError:
                            print("Bitmap Directory not referenced. Please use Default Data")
                    
                    #get scaling data for bitmap
                    Bitmap = get_scale(shaderfile, (Base_Map_M_1_Offset + 0x10 + 0xC + 0x1), len(Bitmap.directory), Bitmap) #uniform scaling 

                    DefaultNeeded = 0            
                else:
                    #bitmap not referenced but might be needed
                    if(is_texture_needed(ShaderItem, "base_map_m_1")):
                        print("")
                        print("[base_map_m_1]")
                        #DirOffset = shaderfile.tell()
                        
                        #clear old bitmap data
                        Bitmap = bitmap()
                        Bitmap.directory = ""
                        Bitmap.type = ""
                        Bitmap.curve_option = 0
                        Bitmap.width = 0
                        Bitmap.height = 0
                        
                        Bitmap.type = "base_map_m_1"
                        Bitmap.directory = correct_default_dir("base_map_m_1")
                        ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                        ShaderItem.bitmap_list.append(Bitmap)
                
                #DETAIL_MAP_M_1 OFFSET
                if (Detail_Map_M_1_Offset != 0):
                    #print("self_illum_map offset: " + str(SelfIllumMap_Offset))
                    print("")
                    print("[detail_map_m_1]") 
                    shaderfile.seek(Detail_Map_M_1_Offset + 0x10 + 0xE + 0x1)
                    
                    #clear old bitmap data
                    Bitmap = bitmap()
                    Bitmap.directory = ""
                    Bitmap.type = ""
                    Bitmap.curve_option = 0
                    Bitmap.width = 0
                    Bitmap.height = 0
                    
                    #save current data
                    Bitmap.directory = get_dir(shaderfile, Detail_Map_M_1_Offset + 0x10 + 0xE + 0x1)
                    print("Dir: " + Bitmap.directory)
                    Bitmap.type = "detail_map_m_1"
                    ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                    ShaderItem.bitmap_list.append(Bitmap)
                    if (Bitmap.directory == "" or Bitmap.directory == " " or Bitmap.directory == "   "):
                         DefaultNeeded = 1 
                
                    if(DefaultNeeded != 1):
                        try:
                            #get Curve for bitmap
                            Bitmap.curve_option = get_bitmap_curve(Tag_Root + Bitmap.directory + ".bitmap")
                            
                            #Get Resolution of bitmap
                            Bitmap.width = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "width")
                            Bitmap.height = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "height")
                        except OSError:
                            print("Bitmap Directory not referenced. Please use Default Data")
                    
                    #get scaling data for bitmap
                    Bitmap = get_scale(shaderfile, (Detail_Map_M_1_Offset + 0x10 + 0xE + 0x1), len(Bitmap.directory), Bitmap) #uniform scaling 

                    DefaultNeeded = 0             
                else:
                    #bitmap not referenced but might be needed
                    if(is_texture_needed(ShaderItem, "detail_map_m_1")):
                        print("")
                        print("[detail_map_m_1]")
                        #DirOffset = shaderfile.tell()
                        
                        #clear old bitmap data
                        Bitmap = bitmap()
                        Bitmap.directory = ""
                        Bitmap.type = ""
                        Bitmap.curve_option = 0
                        Bitmap.width = 0
                        Bitmap.height = 0
                        
                        Bitmap.type = "detail_map_m_1"
                        Bitmap.directory = correct_default_dir("detail_map_m_1")
                        ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                        ShaderItem.bitmap_list.append(Bitmap)
                
                #BUMP_MAP_M_1 OFFSET
                if (Bump_Map_M_1_Offset != 0):
                    #print("self_illum_map offset: " + str(SelfIllumMap_Offset))
                    print("")
                    print("[bump_map_m_1]") 
                    shaderfile.seek(Bump_Map_M_1_Offset + 0x10 + 0xC + 0x1)
                    
                    #clear old bitmap data
                    Bitmap = bitmap()
                    Bitmap.directory = ""
                    Bitmap.type = ""
                    Bitmap.curve_option = 0
                    Bitmap.width = 0
                    Bitmap.height = 0
                    
                    #save current data
                    Bitmap.directory = get_dir(shaderfile, Bump_Map_M_1_Offset + 0x10 + 0xC + 0x1)
                    print("Dir: " + Bitmap.directory)
                    Bitmap.type = "bump_map_m_1"
                    ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                    ShaderItem.bitmap_list.append(Bitmap)
                    if (Bitmap.directory == "" or Bitmap.directory == " " or Bitmap.directory == "   "):
                         DefaultNeeded = 1 
                
                    if(DefaultNeeded != 1):
                        try:
                            #get Curve for bitmap
                            Bitmap.curve_option = get_bitmap_curve(Tag_Root + Bitmap.directory + ".bitmap")
                            
                            #Get Resolution of bitmap
                            Bitmap.width = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "width")
                            Bitmap.height = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "height")
                        except OSError:
                            print("Bitmap Directory not referenced. Please use Default Data")
                    
                    #get scaling data for bitmap
                    Bitmap = get_scale(shaderfile, (Bump_Map_M_1_Offset + 0x10 + 0xC + 0x1), len(Bitmap.directory), Bitmap) #uniform scaling 

                    DefaultNeeded = 0  
                else:
                    #bitmap not referenced but might be needed
                    if(is_texture_needed(ShaderItem, "bump_map_m_1")):
                        print("")
                        print("[bump_map_m_1]")
                        #DirOffset = shaderfile.tell()
                        
                        #clear old bitmap data
                        Bitmap = bitmap()
                        Bitmap.directory = ""
                        Bitmap.type = ""
                        Bitmap.curve_option = 0
                        Bitmap.width = 0
                        Bitmap.height = 0
                        
                        Bitmap.type = "bump_map_m_1"
                        Bitmap.directory = correct_default_dir("bump_map_m_1")
                        ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                        ShaderItem.bitmap_list.append(Bitmap)
                
                #Detail_Bump_M_1_Offset OFFSET
                if (Detail_Bump_M_1_Offset != 0):
                    #print("self_illum_map offset: " + str(SelfIllumMap_Offset))
                    print("")
                    print("[detail_bump_m_1]") 
                    shaderfile.seek(Detail_Bump_M_1_Offset + 0x10 + 0xF + 0x1)
                    
                    #clear old bitmap data
                    Bitmap = bitmap()
                    Bitmap.directory = ""
                    Bitmap.type = ""
                    Bitmap.curve_option = 0
                    Bitmap.width = 0
                    Bitmap.height = 0
                    
                    #save current data
                    Bitmap.directory = get_dir(shaderfile, Detail_Bump_M_1_Offset + 0x10 + 0xF + 0x1)
                    print("Dir: " + Bitmap.directory)
                    Bitmap.type = "detail_bump_m_1"
                    ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                    ShaderItem.bitmap_list.append(Bitmap)
                    if (Bitmap.directory == "" or Bitmap.directory == " " or Bitmap.directory == "   "):
                         DefaultNeeded = 1 
                
                    if(DefaultNeeded != 1):
                        try:
                            #get Curve for bitmap
                            Bitmap.curve_option = get_bitmap_curve(Tag_Root + Bitmap.directory + ".bitmap")
                            
                            #Get Resolution of bitmap
                            Bitmap.width = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "width")
                            Bitmap.height = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "height")
                        except OSError:
                            print("Bitmap Directory not referenced. Please use Default Data")
                    
                    #get scaling data for bitmap
                    Bitmap = get_scale(shaderfile, (Detail_Bump_M_1_Offset + 0x10 + 0xF + 0x1), len(Bitmap.directory), Bitmap) #uniform scaling 

                    DefaultNeeded = 0 
                else:
                    #bitmap not referenced but might be needed
                    if(is_texture_needed(ShaderItem, "detail_bump_m_1")):
                        print("")
                        print("[detail_bump_m_1]")
                        #DirOffset = shaderfile.tell()
                        
                        #clear old bitmap data
                        Bitmap = bitmap()
                        Bitmap.directory = ""
                        Bitmap.type = ""
                        Bitmap.curve_option = 0
                        Bitmap.width = 0
                        Bitmap.height = 0
                        
                        Bitmap.type = "detail_bump_m_1"
                        Bitmap.directory = correct_default_dir("detail_bump_m_1")
                        ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                        ShaderItem.bitmap_list.append(Bitmap)
                
                #BASE_MAP_M_2 OFFSET
                if (Base_Map_M_2_Offset != 0):
                    #print("self_illum_map offset: " + str(SelfIllumMap_Offset))
                    print("")
                    print("[base_map_m_2]") 
                    shaderfile.seek(Base_Map_M_2_Offset + 0x10 + 0xC + 0x1)
                    
                    #clear old bitmap data
                    Bitmap = bitmap()
                    Bitmap.directory = ""
                    Bitmap.type = ""
                    Bitmap.curve_option = 0
                    Bitmap.width = 0
                    Bitmap.height = 0
                    
                    #save current data
                    Bitmap.directory = get_dir(shaderfile, Base_Map_M_2_Offset + 0x10 + 0xC + 0x1)
                    print("Dir: " + Bitmap.directory)
                    Bitmap.type = "base_map_m_2"
                    ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                    ShaderItem.bitmap_list.append(Bitmap)
                    if (Bitmap.directory == "" or Bitmap.directory == " " or Bitmap.directory == "   "):
                         DefaultNeeded = 1 
                
                    if(DefaultNeeded != 1):
                        try:
                            #get Curve for bitmap
                            Bitmap.curve_option = get_bitmap_curve(Tag_Root + Bitmap.directory + ".bitmap")
                            
                            #Get Resolution of bitmap
                            Bitmap.width = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "width")
                            Bitmap.height = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "height")
                        except OSError:
                            print("Bitmap Directory not referenced. Please use Default Data")
                    
                    #get scaling data for bitmap
                    Bitmap = get_scale(shaderfile, (Base_Map_M_2_Offset + 0x10 + 0xC + 0x1), len(Bitmap.directory), Bitmap) #uniform scaling 

                    DefaultNeeded = 0            
                else:
                    #bitmap not referenced but might be needed
                    if(is_texture_needed(ShaderItem, "base_map_m_2")):
                        print("")
                        print("[base_map_m_2]")
                        #DirOffset = shaderfile.tell()
                        
                        #clear old bitmap data
                        Bitmap = bitmap()
                        Bitmap.directory = ""
                        Bitmap.type = ""
                        Bitmap.curve_option = 0
                        Bitmap.width = 0
                        Bitmap.height = 0
                        
                        Bitmap.type = "base_map_m_2"
                        Bitmap.directory = correct_default_dir("base_map_m_2")
                        ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                        ShaderItem.bitmap_list.append(Bitmap)
                
                #DETAIL_MAP_M_2 OFFSET
                if (Detail_Map_M_2_Offset != 0):
                    #print("self_illum_map offset: " + str(SelfIllumMap_Offset))
                    print("")
                    print("[detail_map_m_2]") 
                    shaderfile.seek(Detail_Map_M_2_Offset + 0x10 + 0xE + 0x1)
                    
                    #clear old bitmap data
                    Bitmap = bitmap()
                    Bitmap.directory = ""
                    Bitmap.type = ""
                    Bitmap.curve_option = 0
                    Bitmap.width = 0
                    Bitmap.height = 0
                    
                    #save current data
                    Bitmap.directory = get_dir(shaderfile, Detail_Map_M_2_Offset + 0x10 + 0xE + 0x1)
                    print("Dir: " + Bitmap.directory)
                    Bitmap.type = "detail_map_m_2"
                    ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                    ShaderItem.bitmap_list.append(Bitmap)
                    if (Bitmap.directory == "" or Bitmap.directory == " " or Bitmap.directory == "   "):
                         DefaultNeeded = 1 
                
                    if(DefaultNeeded != 1):
                        try:
                            #get Curve for bitmap
                            Bitmap.curve_option = get_bitmap_curve(Tag_Root + Bitmap.directory + ".bitmap")
                            
                            #Get Resolution of bitmap
                            Bitmap.width = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "width")
                            Bitmap.height = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "height")
                        except OSError:
                            print("Bitmap Directory not referenced. Please use Default Data")
                    
                    #get scaling data for bitmap
                    Bitmap = get_scale(shaderfile, (Detail_Map_M_2_Offset + 0x10 + 0xE + 0x1), len(Bitmap.directory), Bitmap) #uniform scaling 

                    DefaultNeeded = 0             
                else:
                    #bitmap not referenced but might be needed
                    if(is_texture_needed(ShaderItem, "detail_map_m_2")):
                        print("")
                        print("[detail_map_m_2]")
                        #DirOffset = shaderfile.tell()
                        
                        #clear old bitmap data
                        Bitmap = bitmap()
                        Bitmap.directory = ""
                        Bitmap.type = ""
                        Bitmap.curve_option = 0
                        Bitmap.width = 0
                        Bitmap.height = 0
                        
                        Bitmap.type = "detail_map_m_2"
                        Bitmap.directory = correct_default_dir("detail_map_m_2")
                        ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                        ShaderItem.bitmap_list.append(Bitmap)
                
                #BUMP_MAP_M_2 OFFSET
                if (Bump_Map_M_2_Offset != 0):
                    #print("self_illum_map offset: " + str(SelfIllumMap_Offset))
                    print("")
                    print("[bump_map_m_2]") 
                    shaderfile.seek(Bump_Map_M_2_Offset + 0x10 + 0xC + 0x1)
                    
                    #clear old bitmap data
                    Bitmap = bitmap()
                    Bitmap.directory = ""
                    Bitmap.type = ""
                    Bitmap.curve_option = 0
                    Bitmap.width = 0
                    Bitmap.height = 0
                    
                    #save current data
                    Bitmap.directory = get_dir(shaderfile, Bump_Map_M_2_Offset + 0x10 + 0xC + 0x1)
                    print("Dir: " + Bitmap.directory)
                    Bitmap.type = "bump_map_m_2"
                    ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                    ShaderItem.bitmap_list.append(Bitmap)
                    if (Bitmap.directory == "" or Bitmap.directory == " " or Bitmap.directory == "   "):
                         DefaultNeeded = 1 
                
                    if(DefaultNeeded != 1):
                        try:
                            #get Curve for bitmap
                            Bitmap.curve_option = get_bitmap_curve(Tag_Root + Bitmap.directory + ".bitmap")
                            
                            #Get Resolution of bitmap
                            Bitmap.width = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "width")
                            Bitmap.height = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "height")
                        except OSError:
                            print("Bitmap Directory not referenced. Please use Default Data")
                    
                    #get scaling data for bitmap
                    Bitmap = get_scale(shaderfile, (Bump_Map_M_2_Offset + 0x10 + 0xC + 0x1), len(Bitmap.directory), Bitmap) #uniform scaling 

                    DefaultNeeded = 0  
                else:
                    #bitmap not referenced but might be needed
                    if(is_texture_needed(ShaderItem, "bump_map_m_2")):
                        print("")
                        print("[bump_map_m_2]")
                        #DirOffset = shaderfile.tell()
                        
                        #clear old bitmap data
                        Bitmap = bitmap()
                        Bitmap.directory = ""
                        Bitmap.type = ""
                        Bitmap.curve_option = 0
                        Bitmap.width = 0
                        Bitmap.height = 0
                        
                        Bitmap.type = "bump_map_m_2"
                        Bitmap.directory = correct_default_dir("bump_map_m_2")
                        ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                        ShaderItem.bitmap_list.append(Bitmap)
                
                #Detail_Bump_M_3_Offset OFFSET
                if (Detail_Bump_M_3_Offset != 0):
                    #print("self_illum_map offset: " + str(SelfIllumMap_Offset))
                    print("")
                    print("[detail_bump_m_3]") 
                    shaderfile.seek(Detail_Bump_M_3_Offset + 0x10 + 0xF + 0x1)
                    
                    #clear old bitmap data
                    Bitmap = bitmap()
                    Bitmap.directory = ""
                    Bitmap.type = ""
                    Bitmap.curve_option = 0
                    Bitmap.width = 0
                    Bitmap.height = 0
                    
                    #save current data
                    Bitmap.directory = get_dir(shaderfile, Detail_Bump_M_3_Offset + 0x10 + 0xF + 0x1)
                    print("Dir: " + Bitmap.directory)
                    Bitmap.type = "detail_bump_m_3"
                    ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                    ShaderItem.bitmap_list.append(Bitmap)
                    if (Bitmap.directory == "" or Bitmap.directory == " " or Bitmap.directory == "   "):
                         DefaultNeeded = 1 
                
                    if(DefaultNeeded != 1):
                        try:
                            #get Curve for bitmap
                            Bitmap.curve_option = get_bitmap_curve(Tag_Root + Bitmap.directory + ".bitmap")
                            
                            #Get Resolution of bitmap
                            Bitmap.width = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "width")
                            Bitmap.height = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "height")
                        except OSError:
                            print("Bitmap Directory not referenced. Please use Default Data")
                    
                    #get scaling data for bitmap
                    Bitmap = get_scale(shaderfile, (Detail_Bump_M_3_Offset + 0x10 + 0xF + 0x1), len(Bitmap.directory), Bitmap) #uniform scaling 

                    DefaultNeeded = 0 
                else:
                    #bitmap not referenced but might be needed
                    if(is_texture_needed(ShaderItem, "detail_bump_m_3")):
                        print("")
                        print("[detail_bump_m_3]")
                        #DirOffset = shaderfile.tell()
                        
                        #clear old bitmap data
                        Bitmap = bitmap()
                        Bitmap.directory = ""
                        Bitmap.type = ""
                        Bitmap.curve_option = 0
                        Bitmap.width = 0
                        Bitmap.height = 0
                        
                        Bitmap.type = "detail_bump_m_3"
                        Bitmap.directory = correct_default_dir("detail_bump_m_3")
                        ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                        ShaderItem.bitmap_list.append(Bitmap)
                
                #BASE_MAP_M_3 OFFSET
                if (Base_Map_M_3_Offset != 0):
                    #print("self_illum_map offset: " + str(SelfIllumMap_Offset))
                    print("")
                    print("[base_map_m_3]") 
                    shaderfile.seek(Base_Map_M_3_Offset + 0x10 + 0xC + 0x1)
                    
                    #clear old bitmap data
                    Bitmap = bitmap()
                    Bitmap.directory = ""
                    Bitmap.type = ""
                    Bitmap.curve_option = 0
                    Bitmap.width = 0
                    Bitmap.height = 0
                    
                    #save current data
                    Bitmap.directory = get_dir(shaderfile, Base_Map_M_3_Offset + 0x10 + 0xC + 0x1)
                    print("Dir: " + Bitmap.directory)
                    Bitmap.type = "base_map_m_3"
                    ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                    ShaderItem.bitmap_list.append(Bitmap)
                    if (Bitmap.directory == "" or Bitmap.directory == " " or Bitmap.directory == "   "):
                         DefaultNeeded = 1 
                
                    if(DefaultNeeded != 1):
                        try:
                            #get Curve for bitmap
                            Bitmap.curve_option = get_bitmap_curve(Tag_Root + Bitmap.directory + ".bitmap")
                            
                            #Get Resolution of bitmap
                            Bitmap.width = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "width")
                            Bitmap.height = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "height")
                        except OSError:
                            print("Bitmap Directory not referenced. Please use Default Data")
                    
                    #get scaling data for bitmap
                    Bitmap = get_scale(shaderfile, (Base_Map_M_3_Offset + 0x10 + 0xC + 0x1), len(Bitmap.directory), Bitmap) #uniform scaling 

                    DefaultNeeded = 0            
                else:
                    #bitmap not referenced but might be needed
                    if(is_texture_needed(ShaderItem, "base_map_m_3")):
                        print("")
                        print("[base_map_m_3]")
                        #DirOffset = shaderfile.tell()
                        
                        #clear old bitmap data
                        Bitmap = bitmap()
                        Bitmap.directory = ""
                        Bitmap.type = ""
                        Bitmap.curve_option = 0
                        Bitmap.width = 0
                        Bitmap.height = 0
                        
                        Bitmap.type = "base_map_m_3"
                        Bitmap.directory = correct_default_dir("base_map_m_3")
                        ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                        ShaderItem.bitmap_list.append(Bitmap)
                
                #DETAIL_MAP_M_3 OFFSET
                if (Detail_Map_M_3_Offset != 0):
                    #print("self_illum_map offset: " + str(SelfIllumMap_Offset))
                    print("")
                    print("[detail_map_m_3]") 
                    shaderfile.seek(Detail_Map_M_3_Offset + 0x10 + 0xE + 0x1)
                    
                    #clear old bitmap data
                    Bitmap = bitmap()
                    Bitmap.directory = ""
                    Bitmap.type = ""
                    Bitmap.curve_option = 0
                    Bitmap.width = 0
                    Bitmap.height = 0
                    
                    #save current data
                    Bitmap.directory = get_dir(shaderfile, Detail_Map_M_3_Offset + 0x10 + 0xE + 0x1)
                    print("Dir: " + Bitmap.directory)
                    Bitmap.type = "detail_map_m_3"
                    ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                    ShaderItem.bitmap_list.append(Bitmap)
                    if (Bitmap.directory == "" or Bitmap.directory == " " or Bitmap.directory == "   "):
                         DefaultNeeded = 1 
                
                    if(DefaultNeeded != 1):
                        try:
                            #get Curve for bitmap
                            Bitmap.curve_option = get_bitmap_curve(Tag_Root + Bitmap.directory + ".bitmap")
                            
                            #Get Resolution of bitmap
                            Bitmap.width = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "width")
                            Bitmap.height = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "height")
                        except OSError:
                            print("Bitmap Directory not referenced. Please use Default Data")
                    
                    #get scaling data for bitmap
                    Bitmap = get_scale(shaderfile, (Detail_Map_M_3_Offset + 0x10 + 0xE + 0x1), len(Bitmap.directory), Bitmap) #uniform scaling 

                    DefaultNeeded = 0             
                else:
                    #bitmap not referenced but might be needed
                    if(is_texture_needed(ShaderItem, "detail_map_m_3")):
                        print("")
                        print("[detail_map_m_3]")
                        #DirOffset = shaderfile.tell()
                        
                        #clear old bitmap data
                        Bitmap = bitmap()
                        Bitmap.directory = ""
                        Bitmap.type = ""
                        Bitmap.curve_option = 0
                        Bitmap.width = 0
                        Bitmap.height = 0
                        
                        Bitmap.type = "detail_map_m_3"
                        Bitmap.directory = correct_default_dir("detail_map_m_3")
                        ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                        ShaderItem.bitmap_list.append(Bitmap)
                
                #BUMP_MAP_M_3 OFFSET
                if (Bump_Map_M_3_Offset != 0):
                    #print("self_illum_map offset: " + str(SelfIllumMap_Offset))
                    print("")
                    print("[bump_map_m_3]") 
                    shaderfile.seek(Bump_Map_M_3_Offset + 0x10 + 0xC + 0x1)
                    
                    #clear old bitmap data
                    Bitmap = bitmap()
                    Bitmap.directory = ""
                    Bitmap.type = ""
                    Bitmap.curve_option = 0
                    Bitmap.width = 0
                    Bitmap.height = 0
                    
                    #save current data
                    Bitmap.directory = get_dir(shaderfile, Bump_Map_M_3_Offset + 0x10 + 0xC + 0x1)
                    print("Dir: " + Bitmap.directory)
                    Bitmap.type = "bump_map_m_3"
                    ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                    ShaderItem.bitmap_list.append(Bitmap)
                    if (Bitmap.directory == "" or Bitmap.directory == " " or Bitmap.directory == "   "):
                         DefaultNeeded = 1 
                
                    if(DefaultNeeded != 1):
                        try:
                            #get Curve for bitmap
                            Bitmap.curve_option = get_bitmap_curve(Tag_Root + Bitmap.directory + ".bitmap")
                            
                            #Get Resolution of bitmap
                            Bitmap.width = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "width")
                            Bitmap.height = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "height")
                        except OSError:
                            print("Bitmap Directory not referenced. Please use Default Data")
                    
                    #get scaling data for bitmap
                    Bitmap = get_scale(shaderfile, (Bump_Map_M_3_Offset + 0x10 + 0xC + 0x1), len(Bitmap.directory), Bitmap) #uniform scaling 

                    DefaultNeeded = 0  
                else:
                    #bitmap not referenced but might be needed
                    if(is_texture_needed(ShaderItem, "bump_map_m_3")):
                        print("")
                        print("[bump_map_m_3]")
                        #DirOffset = shaderfile.tell()
                        
                        #clear old bitmap data
                        Bitmap = bitmap()
                        Bitmap.directory = ""
                        Bitmap.type = ""
                        Bitmap.curve_option = 0
                        Bitmap.width = 0
                        Bitmap.height = 0
                        
                        Bitmap.type = "bump_map_m_3"
                        Bitmap.directory = correct_default_dir("bump_map_m_3")
                        ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                        ShaderItem.bitmap_list.append(Bitmap)
                
                #Detail_Bump_M_3_Offset OFFSET
                if (Detail_Bump_M_3_Offset != 0):
                    #print("self_illum_map offset: " + str(SelfIllumMap_Offset))
                    print("")
                    print("[detail_bump_m_3]") 
                    shaderfile.seek(Detail_Bump_M_3_Offset + 0x10 + 0xF + 0x1)
                    
                    #clear old bitmap data
                    Bitmap = bitmap()
                    Bitmap.directory = ""
                    Bitmap.type = ""
                    Bitmap.curve_option = 0
                    Bitmap.width = 0
                    Bitmap.height = 0
                    
                    #save current data
                    Bitmap.directory = get_dir(shaderfile, Detail_Bump_M_3_Offset + 0x10 + 0xF + 0x1)
                    print("Dir: " + Bitmap.directory)
                    Bitmap.type = "detail_bump_m_3"
                    ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                    ShaderItem.bitmap_list.append(Bitmap)
                    if (Bitmap.directory == "" or Bitmap.directory == " " or Bitmap.directory == "   "):
                         DefaultNeeded = 1 
                
                    if(DefaultNeeded != 1):
                        try:
                            #get Curve for bitmap
                            Bitmap.curve_option = get_bitmap_curve(Tag_Root + Bitmap.directory + ".bitmap")
                            
                            #Get Resolution of bitmap
                            Bitmap.width = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "width")
                            Bitmap.height = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "height")
                        except OSError:
                            print("Bitmap Directory not referenced. Please use Default Data")
                    
                    #get scaling data for bitmap
                    Bitmap = get_scale(shaderfile, (Detail_Bump_M_3_Offset + 0x10 + 0xF + 0x1), len(Bitmap.directory), Bitmap) #uniform scaling 

                    DefaultNeeded = 0 
                else:
                    #bitmap not referenced but might be needed
                    if(is_texture_needed(ShaderItem, "detail_bump_m_3")):
                        print("")
                        print("[detail_bump_m_3]")
                        #DirOffset = shaderfile.tell()
                        
                        #clear old bitmap data
                        Bitmap = bitmap()
                        Bitmap.directory = ""
                        Bitmap.type = ""
                        Bitmap.curve_option = 0
                        Bitmap.width = 0
                        Bitmap.height = 0
                        
                        Bitmap.type = "detail_bump_m_3"
                        Bitmap.directory = correct_default_dir("detail_bump_m_3")
                        ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                        ShaderItem.bitmap_list.append(Bitmap)

                                                    ##############
                                                    #COLORS/VALUES
                                                    ##############
                #############
                #SHADER FILES
                #############

                #COLOR/SCALE/VALUES    - Might use functions!                 -   CHECK THESE VALUES!!!
                print("")
                print("--[Existing Scaling/Color Values Types]--")
                if (Albedo_Blend_Offset != 0): #float
                    #print("albedo_blend offset: " + str(Albedo_Blend_Offset))
                    
                    
                    #save current data
                    if(has_value(shaderfile, Albedo_Blend_Offset + 0xC + 0x1) == True):
                        ShaderItem.albedo_blend = get_value(shaderfile, Albedo_Blend_Offset + 0xC + 0x1)
                        print("albedo_blend: " + str(ShaderItem.albedo_blend))
                    else:
                        print("albedo_blend value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Albedo_Blend_Offset + 0xC + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Albedo_Blend_Offset + 0xC + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.albedo_blend = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        print("  New Value from function: " + str(ShaderItem.albedo_blend))
                        ShaderItem.function_list.append(FunctionItem)
                        
                if (Albedo_Color_Offset != 0):  #color
                    #print("albedo_color offset: " + str(Albedo_Color_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Albedo_Color_Offset + 0xC + 0x1) == True):
                        ShaderItem.albedo_color = get_rgb(shaderfile, Albedo_Color_Offset + 0xC + 0x1, "rgb")
                        print("albedo_color: " + str(ShaderItem.albedo_color))
                        ShaderItem.albedo_color_alpha = get_rgb(shaderfile, Albedo_Color_Offset + 0xC + 0x1, "alpha")
                        print("albedo_color_alpha: " + str(ShaderItem.albedo_color_alpha))
                    else: #use default value
                        ShaderItem.albedo_color = color_white_rgb
                        print("albedo_color value/color not found. Using Default Value")
                        
                    #check for function                       
                    if(has_function(shaderfile, Albedo_Color_Offset + 0xC + 0x1) == True): #value/color has function
                        FunctionItem = get_color_function_data(shaderfile, Albedo_Color_Offset + 0xC + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with the first color
                        ShaderItem.albedo_color = (FunctionItem.color_1)
                        print("  New Value from function: " + str(ShaderItem.albedo_color))
                        ShaderItem.function_list.append(FunctionItem)      

                if (Bump_Detail_Coefficient_Offset != 0): #float
                    #print("bump_detail_coefficient offset: " + str(Bump_Detail_Coefficient_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Bump_Detail_Coefficient_Offset + 0x17 + 0x1) == True):
                        ShaderItem.bump_detail_coefficient = get_value(shaderfile, Bump_Detail_Coefficient_Offset + 0x17 + 0x1)
                        print("bump_detail_coefficient: " + str(ShaderItem.bump_detail_coefficient))                    
                    else:
                        print("bump_detail_coefficient value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Bump_Detail_Coefficient_Offset + 0x17 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Bump_Detail_Coefficient_Offset + 0x17 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.bump_detail_coefficient = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        print("  New Value from function: " + str(ShaderItem.bump_detail_coefficient))
                        ShaderItem.function_list.append(FunctionItem)
                        
                if (Env_Tint_Color_Offset != 0):  #color
                    #print("env_tint_color offset: " + str(Env_Tint_Color_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Env_Tint_Color_Offset + 0xE + 0x1) == True):
                        ShaderItem.env_tint_color = get_rgb(shaderfile, Env_Tint_Color_Offset + 0xE + 0x1, "rgb")
                        print("env_tint_color: " + str(ShaderItem.env_tint_color))                    
                    else:
                        ShaderItem.env_tint_color = color_white_rgb
                        print("env_tint_color value/color not found")
                        
                    #check for function                       
                    if(has_function(shaderfile, Env_Tint_Color_Offset + 0xE + 0x1) == True): #value/color has function
                        FunctionItem = get_color_function_data(shaderfile, Env_Tint_Color_Offset + 0xE + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with the first color
                        ShaderItem.env_tint_color = (FunctionItem.color_1)
                        print("  New Value from function: " + str(ShaderItem.env_tint_color))
                        ShaderItem.function_list.append(FunctionItem)      
                        
                if (Env_Roughness_Scale_Offset != 0): #float
                    #print("env_roughness_scale offset: " + str(Env_Roughness_Scale_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Env_Roughness_Scale_Offset + 0x13 + 0x1) == True):
                        ShaderItem.env_roughness_scale = get_value(shaderfile, Env_Roughness_Scale_Offset + 0x13 + 0x1)
                        print("env_roughness_scale: " + str(ShaderItem.env_roughness_scale))                    
                    else:
                        print("env_roughness_scale value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Env_Roughness_Scale_Offset + 0x13 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Env_Roughness_Scale_Offset + 0x13 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.env_roughness_scale = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        print("  New Value from function: " + str(ShaderItem.env_roughness_scale))
                        ShaderItem.function_list.append(FunctionItem)                  
                        
                if (Self_Illum_Color_Offset != 0):  #color
                    #print("self_illum_color offset: " + str(Env_Tint_Color_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Self_Illum_Color_Offset + 0x10 + 0x1) == True):
                        ShaderItem.self_illum_color = get_rgb(shaderfile, Self_Illum_Color_Offset + 0x10 + 0x1, "rgb")
                        print("self_illum_color: " + str(ShaderItem.self_illum_color))                    
                    else:
                        print("self_illum_color value/color not found")
                        
                    #check for function                       
                    if(has_function(shaderfile, Self_Illum_Color_Offset + 0x10 + 0x1) == True): #value/color has function
                        FunctionItem = get_color_function_data(shaderfile, Self_Illum_Color_Offset + 0x10 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with the first color
                        ShaderItem.self_illum_color = (FunctionItem.color_1)
                        print("  New Value from function: " + str(ShaderItem.self_illum_color))
                        ShaderItem.function_list.append(FunctionItem)      
                        
                if (Self_Illum_Intensity_Offset != 0): #float
                    #print("self_illum_intensity offset: " + str(Self_Illum_Intensity_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Self_Illum_Intensity_Offset + 0x14 + 0x1) == True):
                        ShaderItem.self_illum_intensity = get_value(shaderfile, Self_Illum_Intensity_Offset + 0x14 + 0x1)
                        print("self_illum_intensity: " + str(ShaderItem.self_illum_intensity))                    
                    else:
                        print("self_illum_intensity value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Self_Illum_Intensity_Offset + 0x14 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Self_Illum_Intensity_Offset + 0x14 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.self_illum_intensity = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        print("  New Value from function: " + str(ShaderItem.self_illum_intensity))
                        ShaderItem.function_list.append(FunctionItem)
                        
                if (Channel_A_Offset != 0):  #color
                    #print("channel_a offset: " + str(Channel_A_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Channel_A_Offset + 0x9 + 0x1) == True):
                        ShaderItem.channel_a = get_rgb(shaderfile, Channel_A_Offset + 0x9 + 0x1, "rgb")
                        print("channel_a: " + str(ShaderItem.channel_a))                    
                    else:
                        print("channel_a value/color not found")
                       
                    #check for function                       
                    if(has_function(shaderfile, Channel_A_Offset + 0x9 + 0x1) == True): #value/color has function
                        FunctionItem = get_color_function_data(shaderfile, Channel_A_Offset + 0x9 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with the first color
                        ShaderItem.channel_a = (FunctionItem.color_1)
                        print("  New Value from function: " + str(ShaderItem.channel_a))
                        ShaderItem.function_list.append(FunctionItem)   
                        
                if (Channel_A_Alpha_Offset != 0): #float
                    #print("channel_a_alpha offset: " + str(Channel_A_Alpha_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Channel_A_Alpha_Offset + 0xF + 0x1) == True):
                        ShaderItem.channel_a_alpha = get_value(shaderfile, Channel_A_Alpha_Offset + 0xF + 0x1)
                        print("channel_a_alpha: " + str(ShaderItem.channel_a_alpha))                    
                    else:
                        print("channel_a_alpha value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Channel_A_Alpha_Offset + 0xF + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Channel_A_Alpha_Offset + 0xF + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.channel_a_alpha = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        print("  New Value from function: " + str(ShaderItem.channel_a_alpha))
                        ShaderItem.function_list.append(FunctionItem)                    
                        
                if (Channel_B_Offset != 0):  #color
                    #print("channel_b offset: " + str(Channel_B_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Channel_B_Offset + 0x9 + 0x1) == True):
                        ShaderItem.channel_b = get_rgb(shaderfile, Channel_B_Offset + 0x9 + 0x1, "rgb")
                        print("channel_b: " + str(ShaderItem.channel_b))                    
                    else:
                        print("channel_b value/color not found")
                        
                    #check for function                       
                    if(has_function(shaderfile, Channel_B_Offset + 0x9 + 0x1) == True): #value/color has function
                        FunctionItem = get_color_function_data(shaderfile, Channel_B_Offset + 0x9 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        
                        #overrite some data for this item with the function data with the first color
                        ShaderItem.channel_b = median_rgba(FunctionItem)
                        
                        
                        print("  New Value from function: " + str(ShaderItem.channel_b))
                        ShaderItem.function_list.append(FunctionItem)     
                    else:
                        print("Channel_B set to default")     
                if (Channel_B_Alpha_Offset != 0): #float
                    #print("channel_b_alpha offset: " + str(Channel_B_Alpha_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Channel_B_Alpha_Offset + 0xF + 0x1) == True):
                        ShaderItem.channel_b_alpha = get_value(shaderfile, Channel_B_Alpha_Offset + 0xF + 0x1)
                        print("channel_b_alpha: " + str(ShaderItem.channel_b_alpha))                    
                    else:
                        print("channel_b_alpha value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Channel_B_Alpha_Offset + 0xF + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Channel_B_Alpha_Offset + 0xF + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.channel_b_alpha = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        print("  New Value from function: " + str(ShaderItem.channel_b_alpha))
                        ShaderItem.function_list.append(FunctionItem)                      
                        
                if (Channel_C_Offset != 0):  #color
                    #print("channel_c offset: " + str(Channel_C_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Channel_C_Offset + 0x9 + 0x1) == True):
                        ShaderItem.channel_c = get_rgb(shaderfile, Channel_C_Offset + 0x9 + 0x1, "rgb")
                        print("channel_c: " + str(ShaderItem.channel_c))                    
                    else:
                        print("channel_c value/color not found")
                        
                    #check for function                       
                    if(has_function(shaderfile, Channel_C_Offset + 0x9 + 0x1) == True): #value/color has function
                        FunctionItem = get_color_function_data(shaderfile, Channel_C_Offset + 0x9 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with the first color
                        ShaderItem.channel_c = (FunctionItem.color_1)
                        print("  New Value from function: " + str(ShaderItem.channel_c))
                        ShaderItem.function_list.append(FunctionItem) 

                if (Channel_C_Alpha_Offset != 0): #float
                    #print("channel_c_alpha offset: " + str(Channel_C_Alpha_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Channel_C_Alpha_Offset + 0xF + 0x1) == True):
                        ShaderItem.channel_c_alpha = get_value(shaderfile, Channel_C_Alpha_Offset + 0xF + 0x1)
                        print("channel_c_alpha: " + str(ShaderItem.channel_c_alpha))                    
                    else:
                        print("channel_c_alpha value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Channel_C_Alpha_Offset + 0xF + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Channel_C_Alpha_Offset + 0xF + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.channel_c_alpha = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        print("  New Value from function: " + str(ShaderItem.channel_c_alpha))
                        ShaderItem.function_list.append(FunctionItem)                     
                        
                if (Color_Medium_Offset != 0):  #color
                    #print("color_medium offset: " + str(Color_Medium_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Color_Medium_Offset + 0xC + 0x1) == True):
                        ShaderItem.color_medium = get_rgb(shaderfile, Color_Medium_Offset + 0xC + 0x1, "rgb")
                        print("color_medium: " + str(ShaderItem.color_medium))                    
                    else:
                        print("color_medium value/color not found")
                        
                    #check for function                       
                    if(has_function(shaderfile, Color_Medium_Offset + 0xC + 0x1) == True): #value/color has function
                        FunctionItem = get_color_function_data(shaderfile, Color_Medium_Offset + 0xC + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with the first color
                        ShaderItem.color_medium = (FunctionItem.color_1)
                        print("  New Value from function: " + str(ShaderItem.color_medium))
                        ShaderItem.function_list.append(FunctionItem)        
                        
                if (Color_Medium_Alpha_Offset != 0): #float
                    #print("color_medium_alpha offset: " + str(Color_Medium_Alpha_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Color_Medium_Alpha_Offset + 0x12 + 0x1) == True):
                        ShaderItem.color_medium_alpha = get_value(shaderfile, Color_Medium_Alpha_Offset + 0x12 + 0x1)
                        print("color_medium_alpha: " + str(ShaderItem.color_medium_alpha))                    
                    else:
                        print("color_medium_alpha value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Color_Medium_Alpha_Offset + 0x12 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Color_Medium_Alpha_Offset + 0x12 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.color_medium_alpha = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        print("  New Value from function: " + str(ShaderItem.color_medium_alpha))
                        ShaderItem.function_list.append(FunctionItem)     
                        
                if (Color_Wide_Offset != 0):  #color
                    #print("color_wide offset: " + str(Color_Wide_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Color_Wide_Offset + 0xA + 0x1) == True):
                        ShaderItem.color_wide = get_rgb(shaderfile, Color_Wide_Offset + 0xA + 0x1, "rgb")
                        print("color_wide: " + str(ShaderItem.color_wide))                    
                    else:
                        print("color_wide value/color not found")
                        
                    #check for function                       
                    if(has_function(shaderfile, Color_Wide_Offset + 0xA + 0x1) == True): #value/color has function
                        FunctionItem = get_color_function_data(shaderfile, Color_Wide_Offset + 0xA + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with the first color
                        ShaderItem.color_wide = (FunctionItem.color_1)
                        print("  New Value from function: " + str(ShaderItem.color_wide))
                        ShaderItem.function_list.append(FunctionItem)   
                        
                if (Color_Wide_Alpha_Offset != 0): #float
                    #print("color_wide_alpha offset: " + str(Color_Wide_Alpha_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Color_Wide_Alpha_Offset + 0x10 + 0x1) == True):
                        ShaderItem.channel_a_alpha = get_value(shaderfile, Color_Wide_Alpha_Offset + 0x10 + 0x1)
                        print("color_wide_alpha: " + str(ShaderItem.color_wide_alpha))                    
                    else:
                        print("color_wide_alpha value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Color_Wide_Alpha_Offset + 0x10 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Color_Wide_Alpha_Offset + 0x10 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.color_wide_alpha = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        print("  New Value from function: " + str(ShaderItem.color_wide_alpha))
                        ShaderItem.function_list.append(FunctionItem)    
                        
                if (Color_Sharp_Offset != 0):  #color
                    #print("color_sharp offset: " + str(Color_Sharp_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Color_Sharp_Offset + 0xB + 0x1) == True):
                        ShaderItem.color_sharp = get_rgb(shaderfile, Color_Sharp_Offset + 0xB + 0x1, "rgb")
                        print("color_sharp: " + str(ShaderItem.color_sharp))                    
                    else:
                        print("color_sharp value/color not found")
                        
                    #check for function                       
                    if(has_function(shaderfile, Color_Sharp_Offset + 0xB + 0x1) == True): #value/color has function
                        FunctionItem = get_color_function_data(shaderfile, Color_Sharp_Offset + 0xB + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with the first color
                        ShaderItem.color_sharp = (FunctionItem.color_1)
                        print("  New Value from function: " + str(ShaderItem.color_sharp))
                        ShaderItem.function_list.append(FunctionItem)    
                        
                if (Color_Sharp_Alpha_Offset != 0): #float
                    #print("color_sharp_alpha offset: " + str(Color_Sharp_Alpha_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Color_Sharp_Alpha_Offset + 0x11 + 0x1) == True):
                        ShaderItem.color_sharp_alpha = get_value(shaderfile, Color_Sharp_Alpha_Offset + 0x11 + 0x1)
                        print("color_sharp_alpha: " + str(ShaderItem.color_sharp_alpha))                    
                    else:
                        print("color_sharp_alpha value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Color_Sharp_Alpha_Offset + 0x11 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Color_Sharp_Alpha_Offset + 0x11 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.color_sharp_alpha = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        print("  New Value from function: " + str(ShaderItem.color_sharp_alpha))
                        ShaderItem.function_list.append(FunctionItem)                     
                        
                if (Thinness_Medium_Offset != 0): #float
                    #print("thinness_medium offset: " + str(Thinness_Medium_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Thinness_Medium_Offset + 0xF + 0x1) == True):
                        ShaderItem.thinness_medium = get_value(shaderfile, Thinness_Medium_Offset + 0xF + 0x1)
                        print("thinness_medium: " + str(ShaderItem.thinness_medium))                    
                    else:
                        print("thinness_medium value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Thinness_Medium_Offset + 0xF + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Thinness_Medium_Offset + 0xF + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.thinness_medium = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        print("  New Value from function: " + str(ShaderItem.thinness_medium))
                        ShaderItem.function_list.append(FunctionItem)                              
                        
                if (Thinness_Wide_Offset != 0): #float
                    #print("thinness_wide offset: " + str(Thinness_Wide_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Thinness_Wide_Offset + 0xD + 0x1) == True):
                        ShaderItem.thinness_wide = get_value(shaderfile, Thinness_Wide_Offset + 0xD + 0x1)
                        print("thinness_wide: " + str(ShaderItem.thinness_wide))                    
                    else:
                        print("thinness_wide value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Thinness_Wide_Offset + 0xD + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Thinness_Wide_Offset + 0xD + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.thinness_wide = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        print("  New Value from function: " + str(ShaderItem.thinness_wide))
                        ShaderItem.function_list.append(FunctionItem)                     
                        
                if (Thinness_Sharp_Offset != 0): #float
                    #print("thinness_sharp offset: " + str(Thinness_Sharp_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Thinness_Sharp_Offset + 0xE + 0x1) == True):
                        ShaderItem.thinness_sharp = get_value(shaderfile, Thinness_Sharp_Offset + 0xE + 0x1)
                        print("thinness_sharp: " + str(ShaderItem.thinness_sharp))                    
                    else:
                        print("thinness_sharp value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Thinness_Sharp_Offset + 0xE + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Thinness_Sharp_Offset + 0xE + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.thinness_sharp = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        print("  New Value from function: " + str(ShaderItem.thinness_sharp))
                        ShaderItem.function_list.append(FunctionItem)                    
                        
                if (Meter_Color_On_Offset != 0):  #color
                    #print("meter_color_on offset: " + str(Meter_Color_On_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Meter_Color_On_Offset + 0xE + 0x1) == True):
                        ShaderItem.meter_color_on = get_rgb(shaderfile, Meter_Color_On_Offset + 0xE + 0x1, "rgb")
                        print("meter_color_on: " + str(ShaderItem.meter_color_on))                    
                    else:
                        print("meter_color_on value/color not found")
                        
                    #check for function                       
                    if(has_function(shaderfile, Meter_Color_On_Offset + 0xE + 0x1) == True): #value/color has function
                        FunctionItem = get_color_function_data(shaderfile, Meter_Color_On_Offset + 0xE + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with the first color
                        ShaderItem.meter_color_on = (FunctionItem.color_1)
                        print("  New Value from function: " + str(ShaderItem.meter_color_on))
                        ShaderItem.function_list.append(FunctionItem)     
                        
                if (Meter_Color_Off_Offset != 0):  #color
                    #print("meter_color_off offset: " + str(Meter_Color_Off_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Meter_Color_Off_Offset + 0xF + 0x1) == True):
                        ShaderItem.meter_color_off = get_rgb(shaderfile, Meter_Color_Off_Offset + 0xF + 0x1, "rgb")
                        print("meter_color_off: " + str(ShaderItem.meter_color_off))                    
                    else:
                        print("meter_color_off value/color not found")
                        
                    #check for function                       
                    if(has_function(shaderfile, Meter_Color_Off_Offset + 0xF + 0x1) == True): #value/color has function
                        FunctionItem = get_color_function_data(shaderfile, Meter_Color_Off_Offset + 0xF + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with the first color
                        ShaderItem.meter_color_off = (FunctionItem.color_1)
                        print("  New Value from function: " + str(ShaderItem.meter_color_off))
                        ShaderItem.function_list.append(FunctionItem)                            
                        
                if (Meter_Value_Offset != 0): #float
                    #print("meter_value offset: " + str(Meter_Value_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Meter_Value_Offset + 0xB + 0x1) == True):
                        ShaderItem.meter_value = get_value(shaderfile, Meter_Value_Offset + 0xB + 0x1)
                        print("meter_value: " + str(ShaderItem.meter_value))                    
                    else:
                        print("meter_value value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Meter_Value_Offset + 0xB + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Meter_Value_Offset + 0xB + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.meter_value = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        print("  New Value from function: " + str(ShaderItem.meter_value))
                        ShaderItem.function_list.append(FunctionItem)                      
                        
                if (Primary_Change_Color_blend_Offset != 0): #float
                    #print("primary_change_color_blend offset: " + str(Primary_Change_Color_blend_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Primary_Change_Color_blend_Offset + 0x1A + 0x1) == True):
                        ShaderItem.primary_change_color_blend = get_value(shaderfile, Primary_Change_Color_blend_Offset + 0x1A + 0x1)
                        print("primary_change_color_blend: " + str(ShaderItem.primary_change_color_blend))                    
                    else:
                        print("primary_change_color_blend value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Primary_Change_Color_blend_Offset + 0x1A + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Primary_Change_Color_blend_Offset + 0x1A + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.primary_change_color_blend = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        print("  New Value from function: " + str(ShaderItem.primary_change_color_blend))
                        ShaderItem.function_list.append(FunctionItem)                     
                        
                if (Height_Scale_Offset != 0): #float
                    #print("height_scale offset: " + str(Height_Scale_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Height_Scale_Offset + 0xC + 0x1) == True):
                        ShaderItem.height_scale = get_value(shaderfile, Height_Scale_Offset + 0xC + 0x1)
                        print("height_scale: " + str(ShaderItem.height_scale))                    
                    else:
                        print("height_scale value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Height_Scale_Offset + 0xC + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Height_Scale_Offset + 0xC + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.height_scale = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        print("  New Value from function: " + str(ShaderItem.height_scale))
                        ShaderItem.function_list.append(FunctionItem)                     
                        
                if (Diffuse_Coefficient_Offset != 0): #float
                    #print("diffuse_coefficient offset: " + str(Diffuse_Coefficient_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Diffuse_Coefficient_Offset + 0x13 + 0x1) == True):
                        ShaderItem.diffuse_coefficient = get_value(shaderfile, Diffuse_Coefficient_Offset + 0x13 + 0x1)
                        print("diffuse_coefficient: " + str(ShaderItem.diffuse_coefficient))                    
                    else:
                        print("diffuse_coefficient value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Diffuse_Coefficient_Offset + 0x13 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Diffuse_Coefficient_Offset + 0x13 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.diffuse_coefficient = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        print("  New Value from function: " + str(ShaderItem.diffuse_coefficient))
                        ShaderItem.function_list.append(FunctionItem)                      
                        
                if (Specular_Coefficient_Offset != 0): #float
                    #print("specular_coefficient offset: " + str(Specular_Coefficient_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Specular_Coefficient_Offset + 0x14 + 0x1) == True):
                        ShaderItem.specular_coefficient = get_value(shaderfile, Specular_Coefficient_Offset + 0x14 + 0x1)
                        print("specular_coefficient: " + str(ShaderItem.specular_coefficient))                    
                    else:
                        print("specular_coefficient value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Specular_Coefficient_Offset + 0x14 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Specular_Coefficient_Offset + 0x14 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.specular_coefficient = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        print("  New Value from function: " + str(ShaderItem.specular_coefficient))
                        ShaderItem.function_list.append(FunctionItem)                      
                        
                if (Specular_Tint_Offset != 0):  #color
                    #print("specular_tint offset: " + str(Specular_Tint_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Specular_Tint_Offset + 0xD + 0x1) == True):
                        ShaderItem.specular_tint = get_rgb(shaderfile, Specular_Tint_Offset + 0xD + 0x1, "rgb")
                        print("specular_tint: " + str(ShaderItem.specular_tint))                    
                    else:
                        ShaderItem.specular_tint = color_white_rgb
                        print("specular_tint value/color not found")
                        
                    #check for function                       
                    if(has_function(shaderfile, Specular_Tint_Offset + 0xD + 0x1) == True): #value/color has function
                        FunctionItem = get_color_function_data(shaderfile, Specular_Tint_Offset + 0xD + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with the first color
                        ShaderItem.specular_tint = (FunctionItem.color_1)
                        print("  New Value from function: " + str(ShaderItem.specular_tint))
                        ShaderItem.function_list.append(FunctionItem)                        
                        
                if (Fresnel_Color_Offset != 0):  #color
                    #print("fresnel_color offset: " + str(Fresnel_Color_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Fresnel_Color_Offset + 0xD + 0x1) == True):
                        ShaderItem.fresnel_color = get_rgb(shaderfile, Fresnel_Color_Offset + 0xD + 0x1, "rgb")
                        print("fresnel_color: " + str(ShaderItem.fresnel_color))                    
                    else:
                        print("fresnel_color value/color not found")
                        
                    #check for function                       
                    if(has_function(shaderfile, Fresnel_Color_Offset + 0xD + 0x1) == True): #value/color has function
                        FunctionItem = get_color_function_data(shaderfile, Fresnel_Color_Offset + 0xD + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with the first color
                        ShaderItem.fresnel_color = (FunctionItem.color_1)
                        print("  New Value from function: " + str(ShaderItem.fresnel_color))
                        ShaderItem.function_list.append(FunctionItem)                      
                        
                if (Roughness_Offset != 0): #float
                    #print("roughness offset: " + str(Roughness_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Roughness_Offset + 0x9 + 0x1) == True):
                        ShaderItem.roughness = get_value(shaderfile, Roughness_Offset + 0x9 + 0x1)
                        print("roughness: " + str(ShaderItem.roughness))                    
                    else:
                        print("roughness value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Roughness_Offset + 0x9 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Roughness_Offset + 0x9 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.roughness = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        print("  New Value from function: " + str(ShaderItem.roughness))
                        ShaderItem.function_list.append(FunctionItem)                    
                        
                if (Environment_Map_Specular_Contribution_Offset != 0): #float
                    #print("environment_map_specular_contribution offset: " + str(Environment_Map_Specular_Contribution_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Environment_Map_Specular_Contribution_Offset + 0x25 + 0x1) == True):
                        ShaderItem.environment_map_specular_contribution = get_value(shaderfile, Environment_Map_Specular_Contribution_Offset + 0x25 + 0x1)
                        print("environment_map_specular_contribution: " + str(ShaderItem.environment_map_specular_contribution))                    
                    else:
                        print("environment_map_specular_contribution value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Environment_Map_Specular_Contribution_Offset + 0x25 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Environment_Map_Specular_Contribution_Offset + 0x25 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.environment_map_specular_contribution = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        print("  New Value from function: " + str(ShaderItem.environment_map_specular_contribution))
                        ShaderItem.function_list.append(FunctionItem)                    
                        
                if (Use_Material_Texture_Offset != 0): #float
                    #print("use_material_texture offset: " + str(Use_Material_Texture_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Use_Material_Texture_Offset + 0x14 + 0x1) == True):
                        ShaderItem.use_material_texture = get_value(shaderfile, Use_Material_Texture_Offset + 0x14 + 0x1)
                        print("use_material_texture: " + str(ShaderItem.use_material_texture))                    
                    else:
                        print("use_material_texture value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Use_Material_Texture_Offset + 0x14 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Use_Material_Texture_Offset + 0x14 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.use_material_texture = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        print("  New Value from function: " + str(ShaderItem.use_material_texture))
                        ShaderItem.function_list.append(FunctionItem)                     
                        
                if (Normal_Specular_Power_Offset != 0): #float
                    #print("normal_specular_power offset: " + str(Normal_Specular_Power_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Normal_Specular_Power_Offset + 0x15 + 0x1) == True):
                        ShaderItem.normal_specular_power = get_value(shaderfile, Normal_Specular_Power_Offset + 0x15 + 0x1)
                        print("normal_specular_power: " + str(ShaderItem.normal_specular_power))                    
                    else:
                        print("normal_specular_power value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Normal_Specular_Power_Offset + 0x15 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Normal_Specular_Power_Offset + 0x15 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.normal_specular_power = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        print("  New Value from function: " + str(ShaderItem.normal_specular_power))
                        ShaderItem.function_list.append(FunctionItem)                    
                        
                if (Normal_Specular_Tint_Offset != 0):  #color
                    #print("normal_specular_tint offset: " + str(Normal_Specular_Tint_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Normal_Specular_Tint_Offset + 0x14 + 0x1) == True):
                        ShaderItem.normal_specular_tint = get_rgb(shaderfile, Normal_Specular_Tint_Offset + 0x14 + 0x1, "rgb")
                        print("normal_specular_tint: " + str(ShaderItem.normal_specular_tint))                    
                    else:
                        print("normal_specular_tint value/color not found")
                                               
                    #check for function                       
                    if(has_function(shaderfile, Normal_Specular_Tint_Offset + 0x14 + 0x1) == True): #value/color has function
                        FunctionItem = get_color_function_data(shaderfile, Normal_Specular_Tint_Offset + 0x14 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with the first color
                        ShaderItem.normal_specular_tint = (FunctionItem.color_1)
                        print("  New Value from function: " + str(ShaderItem.normal_specular_tint))
                        ShaderItem.function_list.append(FunctionItem)  

                        
                if (Glancing_Specular_Power_Offset != 0): #float
                    #print("glancing_specular_power offset: " + str(Glancing_Specular_Power_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Glancing_Specular_Power_Offset + 0x17 + 0x1) == True):
                        ShaderItem.glancing_specular_power = get_value(shaderfile, Glancing_Specular_Power_Offset + 0x17 + 0x1)
                        print("glancing_specular_power: " + str(ShaderItem.glancing_specular_power))                    
                    else:
                        print("glancing_specular_power value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Glancing_Specular_Power_Offset + 0x17 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Glancing_Specular_Power_Offset + 0x17 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.glancing_specular_power = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        print("  New Value from function: " + str(ShaderItem.glancing_specular_power))
                        ShaderItem.function_list.append(FunctionItem)                     
                        
                if (Glancing_Specular_Tint_Offset != 0):  #color
                    #print("glancing_specular_tint offset: " + str(Glancing_Specular_Tint_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Glancing_Specular_Tint_Offset + 0x16 + 0x1) == True):
                        ShaderItem.glancing_specular_tint = get_rgb(shaderfile, Glancing_Specular_Tint_Offset + 0x16 + 0x1, "rgb")
                        print("glancing_specular_tint: " + str(ShaderItem.glancing_specular_tint))                    
                    else:
                        print("glancing_specular_tint value/color not found")
                        
                    #check for function                       
                    if(has_function(shaderfile, Glancing_Specular_Tint_Offset + 0x16 + 0x1) == True): #value/color has function
                        FunctionItem = get_color_function_data(shaderfile, Glancing_Specular_Tint_Offset + 0x16 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with the first color
                        ShaderItem.glancing_specular_tint = (FunctionItem.color_1)
                        print("  New Value from function: " + str(ShaderItem.glancing_specular_tint))
                        ShaderItem.function_list.append(FunctionItem)  

      
                if (Fresnel_Curve_Steepness_Offset != 0): #float
                    #print("fresnel_curve_steepness offset: " + str(Fresnel_Curve_Steepness_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Fresnel_Curve_Steepness_Offset + 0x17 + 0x1) == True):
                        ShaderItem.fresnel_curve_steepness = get_value(shaderfile, Fresnel_Curve_Steepness_Offset + 0x17 + 0x1)
                        print("fresnel_curve_steepness: " + str(ShaderItem.fresnel_curve_steepness))                    
                    else:
                        print("fresnel_curve_steepness value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Fresnel_Curve_Steepness_Offset + 0x17 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Fresnel_Curve_Steepness_Offset + 0x17 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.fresnel_curve_steepness = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        print("  New Value from function: " + str(ShaderItem.fresnel_curve_steepness))
                        ShaderItem.function_list.append(FunctionItem)                      
                        
                if (Albedo_Specular_Tint_Blend_Offset != 0): #float
                    #print("albedo_specular_tint_blend offset: " + str(Albedo_Specular_Tint_Blend_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Albedo_Specular_Tint_Blend_Offset + 0x1A + 0x1) == True):
                        ShaderItem.albedo_specular_tint_blend = get_value(shaderfile, Albedo_Specular_Tint_Blend_Offset + 0x1A + 0x1)
                        print("albedo_specular_tint_blend: " + str(ShaderItem.albedo_specular_tint_blend))                    
                    else:
                        print("albedo_specular_tint_blend value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Albedo_Specular_Tint_Blend_Offset + 0x1A + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Albedo_Specular_Tint_Blend_Offset + 0x1A + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.albedo_specular_tint_blend = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        print("  New Value from function: " + str(ShaderItem.albedo_specular_tint_blend))
                        ShaderItem.function_list.append(FunctionItem)                     
                        
                if (Fresnel_Curve_Bias_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Fresnel_Curve_Bias_Offset + 0x12 + 0x1) == True):
                        ShaderItem.fresnel_curve_bias = get_value(shaderfile, Fresnel_Curve_Bias_Offset + 0x12 + 0x1)
                        print("fresnel_curve_bias: " + str(ShaderItem.fresnel_curve_bias))                    
                    else:
                        print("fresnel_curve_bias value/color not found")

                    #check for function
                    if(has_function(shaderfile, Fresnel_Curve_Bias_Offset + 0x12 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Fresnel_Curve_Bias_Offset + 0x12 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.fresnel_curve_bias = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        print("  New Value from function: " + str(ShaderItem.fresnel_curve_bias))
                        ShaderItem.function_list.append(FunctionItem)   
                        
                if (Fresnel_Coefficient_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Fresnel_Coefficient_Offset + 0x13 + 0x1) == True):
                        ShaderItem.fresnel_curve_bias = get_value(shaderfile, Fresnel_Coefficient_Offset + 0x13 + 0x1)
                        print("fresnel_coefficient: " + str(ShaderItem.fresnel_coefficient))                    
                    else:
                        print("fresnel_coefficient value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Fresnel_Coefficient_Offset + 0x13 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Fresnel_Coefficient_Offset + 0x13 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.fresnel_coefficient = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        print("  New Value from function: " + str(ShaderItem.fresnel_coefficient))
                        ShaderItem.function_list.append(FunctionItem)                     
                        
                if (Analytical_Specular_Contribution_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Analytical_Specular_Contribution_Offset + 0x20 + 0x1) == True):
                        ShaderItem.analytical_specular_contribution = get_value(shaderfile, Analytical_Specular_Contribution_Offset + 0x20 + 0x1)
                        print("analytical_specular_contribution: " + str(ShaderItem.analytical_specular_contribution))                    
                    else:
                        print("analytical_specular_contribution value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Analytical_Specular_Contribution_Offset + 0x20 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Analytical_Specular_Contribution_Offset + 0x20 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.analytical_specular_contribution = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        print("  New Value from function: " + str(ShaderItem.analytical_specular_contribution))
                        ShaderItem.function_list.append(FunctionItem)                      
                        
                        
                ################
                #TERRAIN SHADERS
                ################
                
                if (Global_Albedo_Tint_Offset != 0):  #color
                    #print("global_albedo_tint offset: " + str(Global_Albedo_Tint_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Global_Albedo_Tint_Offset + 0x12 + 0x1) == True):
                        ShaderItem.global_albedo_tint = get_rgb(shaderfile, Global_Albedo_Tint_Offset + 0x12 + 0x1, "rgb")
                        print("global_albedo_tint: " + str(ShaderItem.global_albedo_tint))                    
                    else:
                        print("global_albedo_tint value/color not found")
                        
                    #check for function                       
                    if(has_function(shaderfile, Global_Albedo_Tint_Offset + 0x12 + 0x1) == True): #value/color has function
                        FunctionItem = get_color_function_data(shaderfile, Global_Albedo_Tint_Offset + 0x12 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with the first color
                        ShaderItem.global_albedo_tint = (FunctionItem.color_1)
                        print("  New Value from function: " + str(ShaderItem.global_albedo_tint))
                        ShaderItem.function_list.append(FunctionItem)      
                
                #Material 0
                if (Diffuse_Coefficient_M_0_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Diffuse_Coefficient_M_0_Offset + 0x17 + 0x1) == True):
                        ShaderItem.diffuse_coefficient_m_0 = get_value(shaderfile, Diffuse_Coefficient_M_0_Offset + 0x17 + 0x1)
                        print("diffuse_coefficient_m_0: " + str(ShaderItem.diffuse_coefficient_m_0))                    
                    else:
                        print("diffuse_coefficient_m_0 value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Diffuse_Coefficient_M_0_Offset + 0x17 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Diffuse_Coefficient_M_0_Offset + 0x17 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.diffuse_coefficient_m_0 = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        print("  New Value from function: " + str(ShaderItem.diffuse_coefficient_m_0))
                        ShaderItem.function_list.append(FunctionItem)

                if (Specular_Coefficient_M_0_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Specular_Coefficient_M_0_Offset + 0x18 + 0x1) == True):
                        ShaderItem.specular_coefficient_m_0 = get_value(shaderfile, Specular_Coefficient_M_0_Offset + 0x18 + 0x1)
                        print("specular_coefficient_m_0: " + str(ShaderItem.specular_coefficient_m_0))                    
                    else:
                        print("specular_coefficient_m_0 value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Specular_Coefficient_M_0_Offset + 0x18 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Specular_Coefficient_M_0_Offset + 0x18 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.specular_coefficient_m_0 = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        print("  New Value from function: " + str(ShaderItem.specular_coefficient_m_0))
                        ShaderItem.function_list.append(FunctionItem)

                if (Specular_Power_M_0_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Specular_Power_M_0_Offset + 0x12 + 0x1) == True):
                        ShaderItem.specular_power_m_0 = get_value(shaderfile, Specular_Power_M_0_Offset + 0x12 + 0x1)
                        print("specular_power_m_0: " + str(ShaderItem.specular_power_m_0))                    
                    else:
                        print("specular_power_m_0 value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Specular_Power_M_0_Offset + 0x12 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Specular_Power_M_0_Offset + 0x12 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.specular_power_m_0 = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        print("  New Value from function: " + str(ShaderItem.specular_power_m_0))
                        ShaderItem.function_list.append(FunctionItem)

                if (Specular_Tint_M_0_Offset != 0):  #color
                    #print("global_albedo_tint offset: " + str(Specular_Tint_M_0_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Specular_Tint_M_0_Offset + 0x11 + 0x1) == True):
                        ShaderItem.specular_tint_m_0 = get_rgb(shaderfile, Specular_Tint_M_0_Offset + 0x11 + 0x1, "rgb")
                        print("specular_tint_m_0: " + str(ShaderItem.specular_tint_m_0))                    
                    else:
                        print("specular_tint_m_0 value/color not found")
                        
                    #check for function                       
                    if(has_function(shaderfile, Specular_Tint_M_0_Offset + 0x11 + 0x1) == True): #value/color has function
                        FunctionItem = get_color_function_data(shaderfile, Specular_Tint_M_0_Offset + 0x11 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with the first color
                        ShaderItem.specular_tint_m_0 = (FunctionItem.color_1)
                        print("  New Value from function: " + str(ShaderItem.specular_tint_m_0))
                        ShaderItem.function_list.append(FunctionItem)   

                if (Fresnel_Curve_Steepness_M_0_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Fresnel_Curve_Steepness_M_0_Offset + 0x1B + 0x1) == True):
                        ShaderItem.fresnel_curve_steepness_m_0 = get_value(shaderfile, Fresnel_Curve_Steepness_M_0_Offset + 0x1B + 0x1)
                        print("fresnel_curve_steepness_m_0: " + str(ShaderItem.fresnel_curve_steepness_m_0))                    
                    else:
                        print("fresnel_curve_steepness_m_0 value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Fresnel_Curve_Steepness_M_0_Offset + 0x1B + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Fresnel_Curve_Steepness_M_0_Offset + 0x1B + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.fresnel_curve_steepness_m_0 = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        print("  New Value from function: " + str(ShaderItem.fresnel_curve_steepness_m_0))
                        ShaderItem.function_list.append(FunctionItem)

                if (Area_Specular_Contribution_M_0_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Area_Specular_Contribution_M_0_Offset + 0x1E + 0x1) == True):
                        ShaderItem.area_specular_contribution_m_0 = get_value(shaderfile, Area_Specular_Contribution_M_0_Offset + 0x1E + 0x1)
                        print("area_specular_contribution_m_0: " + str(ShaderItem.area_specular_contribution_m_0))                    
                    else:
                        print("area_specular_contribution_m_0 value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Area_Specular_Contribution_M_0_Offset + 0x1E + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Area_Specular_Contribution_M_0_Offset + 0x1E + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.area_specular_contribution_m_0 = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        print("  New Value from function: " + str(ShaderItem.area_specular_contribution_m_0))
                        ShaderItem.function_list.append(FunctionItem)


                if (Analytical_Specular_Contribution_M_0_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Analytical_Specular_Contribution_M_0_Offset + 0x24 + 0x1) == True):
                        ShaderItem.analytical_specular_contribution_m_0 = get_value(shaderfile, Analytical_Specular_Contribution_M_0_Offset + 0x24 + 0x1)
                        print("analytical_specular_contribution_m_0: " + str(ShaderItem.analytical_specular_contribution_m_0))                    
                    else:
                        print("analytical_specular_contribution_m_0 value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Analytical_Specular_Contribution_M_0_Offset + 0x24 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Analytical_Specular_Contribution_M_0_Offset + 0x24 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.analytical_specular_contribution_m_0 = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        print("  New Value from function: " + str(ShaderItem.analytical_specular_contribution_m_0))
                        ShaderItem.function_list.append(FunctionItem)

                if (Environment_Specular_Contribution_M_0_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Environment_Specular_Contribution_M_0_Offset + 0x25 + 0x1) == True):
                        ShaderItem.environment_specular_contribution_m_0 = get_value(shaderfile, Environment_Specular_Contribution_M_0_Offset + 0x25 + 0x1)
                        print("environment_specular_contribution_m_0: " + str(ShaderItem.environment_specular_contribution_m_0))                    
                    else:
                        print("environment_specular_contribution_m_0 value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Environment_Specular_Contribution_M_0_Offset + 0x25 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Environment_Specular_Contribution_M_0_Offset + 0x25 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.environment_specular_contribution_m_0 = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        print("  New Value from function: " + str(ShaderItem.environment_specular_contribution_m_0))
                        ShaderItem.function_list.append(FunctionItem)

                if (Albedo_Specular_Tint_Blend_M_0_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Albedo_Specular_Tint_Blend_M_0_Offset + 0x1E + 0x1) == True):
                        ShaderItem.albedo_specular_tint_blend_m_0 = get_value(shaderfile, Albedo_Specular_Tint_Blend_M_0_Offset + 0x1E + 0x1)
                        print("albedo_specular_tint_blend_m_0: " + str(ShaderItem.albedo_specular_tint_blend_m_0))                    
                    else:
                        print("albedo_specular_tint_blend_m_0 value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Albedo_Specular_Tint_Blend_M_0_Offset + 0x1E + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Albedo_Specular_Tint_Blend_M_0_Offset + 0x1E + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.albedo_specular_tint_blend_m_0 = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        print("  New Value from function: " + str(ShaderItem.albedo_specular_tint_blend_m_0))
                        ShaderItem.function_list.append(FunctionItem)

                #Material 1
                if (Diffuse_Coefficient_M_1_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Diffuse_Coefficient_M_1_Offset + 0x17 + 0x1) == True):
                        ShaderItem.diffuse_coefficient_m_1 = get_value(shaderfile, Diffuse_Coefficient_M_1_Offset + 0x17 + 0x1)
                        print("diffuse_coefficient_m_1: " + str(ShaderItem.diffuse_coefficient_m_1))                    
                    else:
                        print("diffuse_coefficient_m_1 value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Diffuse_Coefficient_M_1_Offset + 0x17 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Diffuse_Coefficient_M_1_Offset + 0x17 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.diffuse_coefficient_m_1 = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        print("  New Value from function: " + str(ShaderItem.diffuse_coefficient_m_1))
                        ShaderItem.function_list.append(FunctionItem)

                if (Specular_Coefficient_M_1_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Specular_Coefficient_M_1_Offset + 0x18 + 0x1) == True):
                        ShaderItem.specular_coefficient_m_1 = get_value(shaderfile, Specular_Coefficient_M_1_Offset + 0x18 + 0x1)
                        print("specular_coefficient_m_1: " + str(ShaderItem.specular_coefficient_m_1))                    
                    else:
                        print("specular_coefficient_m_1 value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Specular_Coefficient_M_1_Offset + 0x18 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Specular_Coefficient_M_1_Offset + 0x18 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.specular_coefficient_m_1 = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        print("  New Value from function: " + str(ShaderItem.specular_coefficient_m_1))
                        ShaderItem.function_list.append(FunctionItem)

                if (Specular_Power_M_1_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Specular_Power_M_1_Offset + 0x12 + 0x1) == True):
                        ShaderItem.specular_power_m_1 = get_value(shaderfile, Specular_Power_M_1_Offset + 0x12 + 0x1)
                        print("specular_power_m_1: " + str(ShaderItem.specular_power_m_1))                    
                    else:
                        print("specular_power_m_1 value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Specular_Power_M_1_Offset + 0x12 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Specular_Power_M_1_Offset + 0x12 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.specular_power_m_1 = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        print("  New Value from function: " + str(ShaderItem.specular_power_m_1))
                        ShaderItem.function_list.append(FunctionItem)

                if (Specular_Tint_M_1_Offset != 0):  #color
                    #print("global_albedo_tint offset: " + str(Specular_Tint_M_1_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Specular_Tint_M_1_Offset + 0x11 + 0x1) == True):
                        ShaderItem.specular_tint_m_1 = get_rgb(shaderfile, Specular_Tint_M_1_Offset + 0x11 + 0x1, "rgb")
                        print("specular_tint_m_1: " + str(ShaderItem.specular_tint_m_1))                    
                    else:
                        print("specular_tint_m_1 value/color not found")
                        
                    #check for function                       
                    if(has_function(shaderfile, Specular_Tint_M_1_Offset + 0x11 + 0x1) == True): #value/color has function
                        FunctionItem = get_color_function_data(shaderfile, Specular_Tint_M_1_Offset + 0x11 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with the first color
                        ShaderItem.specular_tint_m_1 = (FunctionItem.color_1)
                        print("  New Value from function: " + str(ShaderItem.specular_tint_m_1))
                        ShaderItem.function_list.append(FunctionItem)   

                if (Fresnel_Curve_Steepness_M_1_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Fresnel_Curve_Steepness_M_1_Offset + 0x1B + 0x1) == True):
                        ShaderItem.fresnel_curve_steepness_m_1 = get_value(shaderfile, Fresnel_Curve_Steepness_M_1_Offset + 0x1B + 0x1)
                        print("fresnel_curve_steepness_m_1: " + str(ShaderItem.fresnel_curve_steepness_m_1))                    
                    else:
                        print("fresnel_curve_steepness_m_1 value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Fresnel_Curve_Steepness_M_1_Offset + 0x1B + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Fresnel_Curve_Steepness_M_1_Offset + 0x1B + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.fresnel_curve_steepness_m_1 = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        print("  New Value from function: " + str(ShaderItem.fresnel_curve_steepness_m_1))
                        ShaderItem.function_list.append(FunctionItem)

                if (Area_Specular_Contribution_M_1_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Area_Specular_Contribution_M_1_Offset + 0x1E + 0x1) == True):
                        ShaderItem.area_specular_contribution_m_1 = get_value(shaderfile, Area_Specular_Contribution_M_1_Offset + 0x1E + 0x1)
                        print("area_specular_contribution_m_1: " + str(ShaderItem.area_specular_contribution_m_1))                    
                    else:
                        print("area_specular_contribution_m_1 value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Area_Specular_Contribution_M_1_Offset + 0x1E + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Area_Specular_Contribution_M_1_Offset + 0x1E + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.area_specular_contribution_m_1 = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        print("  New Value from function: " + str(ShaderItem.area_specular_contribution_m_1))
                        ShaderItem.function_list.append(FunctionItem)


                if (Analytical_Specular_Contribution_M_1_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Analytical_Specular_Contribution_M_1_Offset + 0x24 + 0x1) == True):
                        ShaderItem.analytical_specular_contribution_m_1 = get_value(shaderfile, Analytical_Specular_Contribution_M_1_Offset + 0x24 + 0x1)
                        print("analytical_specular_contribution_m_1: " + str(ShaderItem.analytical_specular_contribution_m_1))                    
                    else:
                        print("analytical_specular_contribution_m_1 value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Analytical_Specular_Contribution_M_1_Offset + 0x24 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Analytical_Specular_Contribution_M_1_Offset + 0x24 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.analytical_specular_contribution_m_1 = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        print("  New Value from function: " + str(ShaderItem.analytical_specular_contribution_m_1))
                        ShaderItem.function_list.append(FunctionItem)

                if (Environment_Specular_Contribution_M_1_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Environment_Specular_Contribution_M_1_Offset + 0x25 + 0x1) == True):
                        ShaderItem.environment_specular_contribution_m_1 = get_value(shaderfile, Environment_Specular_Contribution_M_1_Offset + 0x25 + 0x1)
                        print("environment_specular_contribution_m_1: " + str(ShaderItem.environment_specular_contribution_m_1))                    
                    else:
                        print("environment_specular_contribution_m_1 value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Environment_Specular_Contribution_M_1_Offset + 0x25 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Environment_Specular_Contribution_M_1_Offset + 0x25 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.environment_specular_contribution_m_1 = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        print("  New Value from function: " + str(ShaderItem.environment_specular_contribution_m_1))
                        ShaderItem.function_list.append(FunctionItem)

                if (Albedo_Specular_Tint_Blend_M_1_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Albedo_Specular_Tint_Blend_M_1_Offset + 0x1E + 0x1) == True):
                        ShaderItem.albedo_specular_tint_blend_m_1 = get_value(shaderfile, Albedo_Specular_Tint_Blend_M_1_Offset + 0x1E + 0x1)
                        print("albedo_specular_tint_blend_m_1: " + str(ShaderItem.albedo_specular_tint_blend_m_1))                    
                    else:
                        print("albedo_specular_tint_blend_m_1 value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Albedo_Specular_Tint_Blend_M_1_Offset + 0x1E + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Albedo_Specular_Tint_Blend_M_1_Offset + 0x1E + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.albedo_specular_tint_blend_m_1 = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        print("  New Value from function: " + str(ShaderItem.albedo_specular_tint_blend_m_1))
                        ShaderItem.function_list.append(FunctionItem)
                        
                #Material 2        
                if (Diffuse_Coefficient_M_2_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Diffuse_Coefficient_M_2_Offset + 0x17 + 0x1) == True):
                        ShaderItem.diffuse_coefficient_m_2 = get_value(shaderfile, Diffuse_Coefficient_M_2_Offset + 0x17 + 0x1)
                        print("diffuse_coefficient_m_2: " + str(ShaderItem.diffuse_coefficient_m_2))                    
                    else:
                        print("diffuse_coefficient_m_2 value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Diffuse_Coefficient_M_2_Offset + 0x17 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Diffuse_Coefficient_M_2_Offset + 0x17, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.diffuse_coefficient_m_2 = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        print("  New Value from function: " + str(ShaderItem.diffuse_coefficient_m_2))
                        ShaderItem.function_list.append(FunctionItem)

                if (Specular_Coefficient_M_2_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Specular_Coefficient_M_2_Offset + 0x18 + 0x1) == True):
                        ShaderItem.specular_coefficient_m_2 = get_value(shaderfile, Specular_Coefficient_M_2_Offset + 0x18 + 0x1)
                        print("specular_coefficient_m_2: " + str(ShaderItem.specular_coefficient_m_2))                    
                    else:
                        print("specular_coefficient_m_2 value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Specular_Coefficient_M_2_Offset + 0x18 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Specular_Coefficient_M_2_Offset + 0x18 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.specular_coefficient_m_2 = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        print("  New Value from function: " + str(ShaderItem.specular_coefficient_m_2))
                        ShaderItem.function_list.append(FunctionItem)

                if (Specular_Power_M_2_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Specular_Power_M_2_Offset + 0x12 + 0x1) == True):
                        ShaderItem.specular_power_m_2 = get_value(shaderfile, Specular_Power_M_2_Offset + 0x12 + 0x1)
                        print("specular_power_m_2: " + str(ShaderItem.specular_power_m_2))                    
                    else:
                        print("specular_power_m_2 value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Specular_Power_M_2_Offset + 0x12 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Specular_Power_M_2_Offset + 0x12 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.specular_power_m_2 = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        print("  New Value from function: " + str(ShaderItem.specular_power_m_2))
                        ShaderItem.function_list.append(FunctionItem)

                if (Specular_Tint_M_2_Offset != 0):  #color
                    #print("global_albedo_tint offset: " + str(Specular_Tint_M_2_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Specular_Tint_M_2_Offset + 0x11 + 0x1) == True):
                        ShaderItem.specular_tint_m_2 = get_rgb(shaderfile, Specular_Tint_M_2_Offset + 0x11 + 0x1, "rgb")
                        print("specular_tint_m_2: " + str(ShaderItem.specular_tint_m_2))                    
                    else:
                        print("specular_tint_m_2 value/color not found")
                        
                    #check for function                       
                    if(has_function(shaderfile, Specular_Tint_M_2_Offset + 0x11 + 0x1) == True): #value/color has function
                        FunctionItem = get_color_function_data(shaderfile, Specular_Tint_M_2_Offset + 0x11 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with the first color
                        ShaderItem.specular_tint_m_2 = (FunctionItem.color_1)
                        print("  New Value from function: " + str(ShaderItem.specular_tint_m_2))
                        ShaderItem.function_list.append(FunctionItem)    

                if (Fresnel_Curve_Steepness_M_2_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Fresnel_Curve_Steepness_M_2_Offset + 0x1B + 0x1) == True):
                        ShaderItem.fresnel_curve_steepness_m_2 = get_value(shaderfile, Fresnel_Curve_Steepness_M_2_Offset + 0x1B + 0x1)
                        print("fresnel_curve_steepness_m_2: " + str(ShaderItem.fresnel_curve_steepness_m_2))                    
                    else:
                        print("fresnel_curve_steepness_m_2 value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Fresnel_Curve_Steepness_M_2_Offset + 0x1B + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Fresnel_Curve_Steepness_M_2_Offset + 0x1B + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.fresnel_curve_steepness_m_2 = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        print("  New Value from function: " + str(ShaderItem.fresnel_curve_steepness_m_2))
                        ShaderItem.function_list.append(FunctionItem)

                if (Area_Specular_Contribution_M_2_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Area_Specular_Contribution_M_2_Offset + 0x1E + 0x1) == True):
                        ShaderItem.area_specular_contribution_m_2 = get_value(shaderfile, Area_Specular_Contribution_M_2_Offset + 0x1E + 0x1)
                        print("area_specular_contribution_m_2: " + str(ShaderItem.area_specular_contribution_m_2))                    
                    else:
                        print("area_specular_contribution_m_2 value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Area_Specular_Contribution_M_2_Offset + 0x1E + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Area_Specular_Contribution_M_2_Offset + 0x1E + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.area_specular_contribution_m_2 = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        print("  New Value from function: " + str(ShaderItem.area_specular_contribution_m_2))
                        ShaderItem.function_list.append(FunctionItem)


                if (Analytical_Specular_Contribution_M_2_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Analytical_Specular_Contribution_M_2_Offset + 0x24 + 0x1) == True):
                        ShaderItem.analytical_specular_contribution_m_2 = get_value(shaderfile, Analytical_Specular_Contribution_M_2_Offset + 0x24 + 0x1)
                        print("analytical_specular_contribution_m_2: " + str(ShaderItem.analytical_specular_contribution_m_2))                    
                    else:
                        print("analytical_specular_contribution_m_2 value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Analytical_Specular_Contribution_M_2_Offset + 0x24 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Analytical_Specular_Contribution_M_2_Offset + 0x24 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.analytical_specular_contribution_m_2 = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        print("  New Value from function: " + str(ShaderItem.analytical_specular_contribution_m_2))
                        ShaderItem.function_list.append(FunctionItem)

                if (Environment_Specular_Contribution_M_2_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Environment_Specular_Contribution_M_2_Offset + 0x25 + 0x1) == True):
                        ShaderItem.environment_specular_contribution_m_2 = get_value(shaderfile, Environment_Specular_Contribution_M_2_Offset + 0x25 + 0x1)
                        print("environment_specular_contribution_m_2: " + str(ShaderItem.environment_specular_contribution_m_2))                    
                    else:
                        print("environment_specular_contribution_m_2 value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Environment_Specular_Contribution_M_2_Offset + 0x25 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Environment_Specular_Contribution_M_2_Offset + 0x25 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.environment_specular_contribution_m_2 = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        print("  New Value from function: " + str(ShaderItem.environment_specular_contribution_m_2))
                        ShaderItem.function_list.append(FunctionItem)

                if (Albedo_Specular_Tint_Blend_M_2_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Albedo_Specular_Tint_Blend_M_2_Offset + 0x1E + 0x1) == True):
                        ShaderItem.albedo_specular_tint_blend_m_2 = get_value(shaderfile, Albedo_Specular_Tint_Blend_M_2_Offset + 0x1E + 0x1)
                        print("albedo_specular_tint_blend_m_2: " + str(ShaderItem.albedo_specular_tint_blend_m_2))                    
                    else:
                        print("albedo_specular_tint_blend_m_2 value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Albedo_Specular_Tint_Blend_M_2_Offset + 0x1E + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Albedo_Specular_Tint_Blend_M_2_Offset + 0x1E + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.albedo_specular_tint_blend_m_2 = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        print("  New Value from function: " + str(ShaderItem.albedo_specular_tint_blend_m_2))
                        ShaderItem.function_list.append(FunctionItem)

                #Material 3
                if (Diffuse_Coefficient_M_3_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Diffuse_Coefficient_M_3_Offset + 0x17 + 0x1) == True):
                        ShaderItem.diffuse_coefficient_m_3 = get_value(shaderfile, Diffuse_Coefficient_M_3_Offset + 0x17 + 0x1)
                        print("diffuse_coefficient_m_3: " + str(ShaderItem.diffuse_coefficient_m_3))                    
                    else:
                        print("diffuse_coefficient_m_3 value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Diffuse_Coefficient_M_3_Offset + 0x17 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Diffuse_Coefficient_M_3_Offset + 0x17 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.diffuse_coefficient_m_3 = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        print("  New Value from function: " + str(ShaderItem.diffuse_coefficient_m_3))
                        ShaderItem.function_list.append(FunctionItem)

                if (Specular_Coefficient_M_3_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Specular_Coefficient_M_3_Offset + 0x18 + 0x1) == True):
                        ShaderItem.specular_coefficient_m_3 = get_value(shaderfile, Specular_Coefficient_M_3_Offset + 0x18 + 0x1)
                        print("specular_coefficient_m_3: " + str(ShaderItem.specular_coefficient_m_3))                    
                    else:
                        print("specular_coefficient_m_3 value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Specular_Coefficient_M_3_Offset + 0x18 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Specular_Coefficient_M_3_Offset + 0x18 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.specular_coefficient_m_3 = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        print("  New Value from function: " + str(ShaderItem.specular_coefficient_m_3))
                        ShaderItem.function_list.append(FunctionItem)

                if (Specular_Power_M_3_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Specular_Power_M_3_Offset + 0x12 + 0x1) == True):
                        ShaderItem.specular_power_m_3 = get_value(shaderfile, Specular_Power_M_3_Offset + 0x12 + 0x1)
                        print("specular_power_m_3: " + str(ShaderItem.specular_power_m_3))                    
                    else:
                        print("specular_power_m_3 value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Specular_Power_M_3_Offset + 0x12 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Specular_Power_M_3_Offset + 0x12 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.specular_power_m_3 = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        print("  New Value from function: " + str(ShaderItem.specular_power_m_3))
                        ShaderItem.function_list.append(FunctionItem)

                if (Specular_Tint_M_3_Offset != 0):  #color
                    #print("global_albedo_tint offset: " + str(Specular_Tint_M_3_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Specular_Tint_M_3_Offset + 0x11 + 0x1) == True):
                        ShaderItem.specular_tint_m_3 = get_rgb(shaderfile, Specular_Tint_M_3_Offset + 0x11 + 0x1, "rgb")
                        print("specular_tint_m_3: " + str(ShaderItem.specular_tint_m_3))                    
                    else:
                        print("specular_tint_m_3 value/color not found")
                        
                    #check for function 
                    if(has_function(shaderfile, Specular_Tint_M_3_Offset + 0x11 + 0x1) == True): #value/color has function
                        FunctionItem = get_color_function_data(shaderfile, Specular_Tint_M_3_Offset + 0x11 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with the first color
                        ShaderItem.specular_tint_m_3 = (FunctionItem.color_1)
                        print("  New Value from function: " + str(ShaderItem.specular_tint_m_3))
                        ShaderItem.function_list.append(FunctionItem)

                if (Fresnel_Curve_Steepness_M_3_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Fresnel_Curve_Steepness_M_3_Offset + 0x1B + 0x1) == True):
                        ShaderItem.fresnel_curve_steepness_m_3 = get_value(shaderfile, Fresnel_Curve_Steepness_M_3_Offset + 0x1B + 0x1)
                        print("fresnel_curve_steepness_m_3: " + str(ShaderItem.fresnel_curve_steepness_m_3))                    
                    else:
                        print("fresnel_curve_steepness_m_3 value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Fresnel_Curve_Steepness_M_3_Offset + 0x1B + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Fresnel_Curve_Steepness_M_3_Offset + 0x1B + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.fresnel_curve_steepness_m_3 = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        print("  New Value from function: " + str(ShaderItem.fresnel_curve_steepness_m_3))
                        ShaderItem.function_list.append(FunctionItem)

                if (Area_Specular_Contribution_M_3_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Area_Specular_Contribution_M_3_Offset + 0x1E + 0x1) == True):
                        ShaderItem.area_specular_contribution_m_3 = get_value(shaderfile, Area_Specular_Contribution_M_3_Offset + 0x1E + 0x1)
                        print("area_specular_contribution_m_3: " + str(ShaderItem.area_specular_contribution_m_3))                    
                    else:
                        print("area_specular_contribution_m_3 value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Area_Specular_Contribution_M_3_Offset + 0x1E + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Area_Specular_Contribution_M_3_Offset + 0x1E + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.area_specular_contribution_m_3 = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        print("  New Value from function: " + str(ShaderItem.area_specular_contribution_m_3))
                        ShaderItem.function_list.append(FunctionItem)


                if (Analytical_Specular_Contribution_M_3_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Analytical_Specular_Contribution_M_3_Offset + 0x24 + 0x1) == True):
                        ShaderItem.analytical_specular_contribution_m_3 = get_value(shaderfile, Analytical_Specular_Contribution_M_3_Offset + 0x24 + 0x1)
                        print("analytical_specular_contribution_m_3: " + str(ShaderItem.analytical_specular_contribution_m_3))                    
                    else:
                        print("analytical_specular_contribution_m_3 value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Analytical_Specular_Contribution_M_3_Offset + 0x24 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Analytical_Specular_Contribution_M_3_Offset + 0x24 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.analytical_specular_contribution_m_3 = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        print("  New Value from function: " + str(ShaderItem.analytical_specular_contribution_m_3))
                        ShaderItem.function_list.append(FunctionItem)

                if (Environment_Specular_Contribution_M_3_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Environment_Specular_Contribution_M_3_Offset + 0x25 + 0x1) == True):
                        ShaderItem.environment_specular_contribution_m_3 = get_value(shaderfile, Environment_Specular_Contribution_M_3_Offset + 0x25 + 0x1)
                        print("environment_specular_contribution_m_3: " + str(ShaderItem.environment_specular_contribution_m_3))                    
                    else:
                        print("environment_specular_contribution_m_3 value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Environment_Specular_Contribution_M_3_Offset + 0x25 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Environment_Specular_Contribution_M_3_Offset + 0x25 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.environment_specular_contribution_m_3 = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        print("  New Value from function: " + str(ShaderItem.environment_specular_contribution_m_3))
                        ShaderItem.function_list.append(FunctionItem)

                if (Albedo_Specular_Tint_Blend_M_3_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Albedo_Specular_Tint_Blend_M_3_Offset + 0x1E + 0x1) == True):
                        ShaderItem.albedo_specular_tint_blend_m_3 = get_value(shaderfile, Albedo_Specular_Tint_Blend_M_3_Offset + 0x1E + 0x1)
                        print("albedo_specular_tint_blend_m_3: " + str(ShaderItem.albedo_specular_tint_blend_m_3))                    
                    else:
                        print("albedo_specular_tint_blend_m_3 value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Albedo_Specular_Tint_Blend_M_3_Offset + 0x1E + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Albedo_Specular_Tint_Blend_M_3_Offset + 0x1E + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.albedo_specular_tint_blend_m_3 = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        print("  New Value from function: " + str(ShaderItem.albedo_specular_tint_blend_m_3))
                        ShaderItem.function_list.append(FunctionItem)                    

                            ######################
                            #GATHER WRAP MODE INFO
                            ######################
        
                #ShaderItem.wrap_mode_list = get_wrap_mode_list(shaderfile, Shader_Type, ShaderItem.wrap_mode_list)                    
                ShaderItem = get_wrap_mode_list(shaderfile, Shader_Type, ShaderItem)                    

                print("built wrap_mode_list")           
                shaderfile.close()
                
                
                #search for shader file in directory
                
                #open file in rb mode
                
                #build all data from shader file
                    #bitmap count
                    #list of Bitmap class object
                        #name of bitmap
                        #directory of bitmap
                        #bitmap curve option
                
                #Set Blend Method of Material
                if(Shader_Type == 0): #if .shader file
                    if (ShaderItem.blend_mode_option == 0):
                        pymat_copy.blend_method = 'OPAQUE'
                    elif (ShaderItem.blend_mode_option == 1):
                        pymat_copy.blend_method = Preferred_Blend
                    elif (ShaderItem.blend_mode_option == 3 or ShaderItem.blend_mode_option == 5):
                        pymat_copy.blend_method = Preferred_Blend
                    else:
                        pymat_copy.blend_method = 'OPAQUE'
                        
                    if (ShaderItem.alpha_test_option == 1):
                        pymat_copy.blend_method = Preferred_Blend 
                
                if (Shader_Type == 2):
                    pymat_copy.blend_method = Preferred_Blend
                #instantiate_group(bpy.context.object.material_slots[0].material.node_tree.nodes, 'NodeGroup')    
                    
                print("Bitmap Count: " + str(ShaderItem.bitmap_count)) 
                print("")
                print("")        
                pymat_copy.use_nodes = True
                print("  Clearing Old Nodes-------------------------------------------------------")
                pymat_copy.node_tree.nodes.clear() #clear all nodes from the current tree
                
                
                
                # #location
                # imgtx1.location = Vector((200.0, 400.0))

                # imgtx2.location.x = 100
                # imgtx2.location.y = 200

                # #size
                # # only width changes are allowed within the values of 
                # # node.bl_width_min and node.bl_width_max
                # imgtx2.width = 200
                # imgtx2.width_hidden = 100
                
                #Texture.hide = True         collapses the nodes
                
                #Global variables for node placement
                last_node_x = 0.00
                last_node_y = 0.00
                end_group_x = 0.00
                end_group_y = 0.00
                mat_group_x = 0.00
                mat_group_y = 0.00
                alb_group_x = 0.00
                alb_group_y = 0.00
                bump_group_x = 0.00
                bump_group_y = 0.00
                terr_group_x = 0.00
                terr_group_y = 0.00
                last_texture_x = 0.00
                last_texture_y = 0.00
                
                before_no_tex_x = 0.00
                before_no_tex_y = 0.00
                
                albedo_group_made = 0
                mat_group_made = 0
                bump_group_made = 0
                env_group_made = 0
                illum_group_made = 0
                texture_node_made = 0
                gamma_node_made = 0
                mirror_node_made = 0
                trans_node_made = 0    
                
                
                 
                #Function for making bigger node groups
                def instantiate_group(nodes, data_block_name):
                    group = nodes.new(type='ShaderNodeGroup')
                    group.node_tree = bpy.data.node_groups[data_block_name]
                    return group


                                    ############################    
                                    #Material Output Node Create
                                    ############################
                ############
                #all shaders
                ############
                
                pymat_copy.node_tree.nodes.new('ShaderNodeOutputMaterial')
                material_output = pymat_copy.node_tree.nodes.get("Material Output")
                
                print("Count of Shader Outputs: " + str(ShaderOutputCount))    

                #locations of group    
                last_node_x = material_output.location.x
                last_node_y = material_output.location.y

                                    #########################
                                    #Alpha Blend Group Create
                                    #########################
                #.shader files and .shader_halogram
                if((Shader_Type == 0 or Shader_Type == 3) and (ShaderItem.blend_mode_option == 3 or ShaderItem.blend_mode_option == 5)):
                    AlphaBlendGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: blend_mode - alpha_blend")

                    #locations of group
                    AlphaBlendGroup.location.x = last_node_x - ALPHA_BLEND_HORIZONTAL_SPACING
                    AlphaBlendGroup.location.y = last_node_y
                        
                    last_node_x = AlphaBlendGroup.location.x
                    last_node_y = AlphaBlendGroup.location.y
                    

                                    ########################
                                    #Alpha Test Group Create
                                    ########################
                # .shader files                           #if alpha_test is simple
                if((Shader_Type == 0 or Shader_Type == 2) and (ShaderItem.alpha_test_option == 1)): #H3Category: alpha_test - simple 
                    AlphaTestGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: alpha_test - simple")

                    #locations of group
                    AlphaTestGroup.location.x = last_node_x - ALPHA_TEST_HORIZONTAL_SPACING
                    AlphaTestGroup.location.y = last_node_y
                        
                    last_node_x = AlphaTestGroup.location.x
                    last_node_y = AlphaTestGroup.location.y

                                    ######################
                                    #Additive Group Create
                                    ######################
                # .shader files
                if((Shader_Type == 0 or Shader_Type == 3) and ShaderItem.blend_mode_option == 1):
                    AdditiveGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: blend_mode - additive")
                    
                    #locations of group
                    AdditiveGroup.location.x = last_node_x - ADDITIVE_GROUP_HORIZONTAL_SPACING
                    AdditiveGroup.location.y = last_node_y
                        
                    last_node_x = AdditiveGroup.location.x
                    last_node_y = AdditiveGroup.location.y






                                    #  SHADER OUTPUT FIXING
                                    #############################
                                    #environment map group create
                                    #############################
                ###############
                # .shader files
                ###############
                
                if(Shader_Type == 0 and ShaderItem.environment_mapping_option == 1): #H3Category: environment_mapping - per_pixel
                    ShaderOutputCount = ShaderOutputCount + 1
                elif(Shader_Type == 0 and ShaderItem.environment_mapping_option == 2): #H3Category: environment_mapping - dynamic
                    ShaderOutputCount = ShaderOutputCount + 1

                                    ########################
                                    #self illum group create
                                    ########################
                ###############
                # .shader files
                ###############
                
                if(Shader_Type == 0 and ShaderItem.self_illumination_option == 1): #H3Category: self_illumination - simple
                    ShaderOutputCount = ShaderOutputCount + 1
                elif(Shader_Type == 0 and ShaderItem.self_illumination_option == 2): #H3Category: self_illumination - 3_channel_self_illum
                    ShaderOutputCount = ShaderOutputCount + 1
                elif(Shader_Type == 0 and ShaderItem.self_illumination_option == 3): #H3Category: self_illumination - plasma
                    ShaderOutputCount = ShaderOutputCount + 1
                elif(Shader_Type == 0 and ShaderItem.self_illumination_option == 4): #H3Category: self_illumination - from_diffuse
                    ShaderOutputCount = ShaderOutputCount + 1
                elif(Shader_Type == 0 and ShaderItem.self_illumination_option == 5): #H3Category: self_illumination - illum_detail
                    ShaderOutputCount = ShaderOutputCount + 1
                elif(Shader_Type == 0 and ShaderItem.self_illumination_option == 6): #H3Category: self_illumination - meter
                    ShaderOutputCount = ShaderOutputCount + 1
                elif(Shader_Type == 0 and ShaderItem.self_illumination_option == 7): #H3Category: self_illumination - self_illum_times_diffuse
                    ShaderOutputCount = ShaderOutputCount + 1
                    
                ########################
                # .shader_halogram files
                ########################
                
                if(Shader_Type == 3 and ShaderItem.self_illumination_option == 1): #H3Category: self_illumination - simple
                    ShaderOutputCount = ShaderOutputCount + 1
                elif(Shader_Type == 3 and ShaderItem.self_illumination_option == 2): #H3Category: self_illumination - 3_channel_self_illum
                    ShaderOutputCount = ShaderOutputCount + 1
                elif(Shader_Type == 3 and ShaderItem.self_illumination_option == 3): #H3Category: self_illumination - plasma
                    ShaderOutputCount = ShaderOutputCount + 1
                elif(Shader_Type == 3 and ShaderItem.self_illumination_option == 4): #H3Category: self_illumination - from_diffuse
                    ShaderOutputCount = ShaderOutputCount + 1
                elif(Shader_Type == 3 and ShaderItem.self_illumination_option == 5): #H3Category: self_illumination - illum_detail
                    ShaderOutputCount = ShaderOutputCount + 1
                elif(Shader_Type == 3 and ShaderItem.self_illumination_option == 6): #H3Category: self_illumination - meter
                    ShaderOutputCount = ShaderOutputCount + 1
                elif(Shader_Type == 3 and ShaderItem.self_illumination_option == 7): #H3Category: self_illumination - self_illum_times_diffuse
                    ShaderOutputCount = ShaderOutputCount + 1    
                elif(Shader_Type == 3 and ShaderItem.self_illumination_option == 8): #H3Category: self_illumination - multilayer_additive
                    ShaderOutputCount = ShaderOutputCount + 1  
                elif(Shader_Type == 3 and ShaderItem.self_illumination_option == 9): #H3Category: self_illumination - scope_blur
                    ShaderOutputCount = ShaderOutputCount + 1  
                elif(Shader_Type == 3 and ShaderItem.self_illumination_option == 10): #H3Category: self_illumination - ml_add_four_change_color
                    ShaderOutputCount = ShaderOutputCount + 1  
                elif(Shader_Type == 3 and ShaderItem.self_illumination_option == 11): #H3Category: self_illumination - ml_add_five_change_color
                    ShaderOutputCount = ShaderOutputCount + 1  
                elif(Shader_Type == 3 and ShaderItem.self_illumination_option == 12): #H3Category: self_illumination - plasma_wide_and_sharp_five_change_color
                    ShaderOutputCount = ShaderOutputCount + 1  
                elif(Shader_Type == 3 and ShaderItem.self_illumination_option == 13): #H3Category: self_illumination - self_illum_holograms
                    ShaderOutputCount = ShaderOutputCount + 1  
                    
                                    ############################
                                    #material model group create
                                    ############################
                ###############
                # .shader files
                ###############
                
                if((Shader_Type == 0 or Shader_Type == 2) and ShaderItem.material_model_option == 0): #H3Category: materrial_model - diffuse_only
                    ShaderOutputCount = ShaderOutputCount + 1
                elif(Shader_Type == 0 and ShaderItem.material_model_option == 1): #H3Category: material_model - cook_torrance
                    ShaderOutputCount = ShaderOutputCount + 1
                elif(Shader_Type == 0 and ShaderItem.material_model_option == 2): #H3Category: material_model - two_lobe_phong
                    ShaderOutputCount = ShaderOutputCount + 1
                elif(Shader_Type == 0 and ShaderItem.material_model_option == 3): #H3Category: material_model - foliage                           #Using Diffuse Only FOR NOW FIX LATER
                    ShaderOutputCount = ShaderOutputCount + 1
                elif(Shader_Type == 0 and ShaderItem.material_model_option == 4): #H3Category: material_model - two_lobe_phong
                    print("Mat Model Option: none")
                elif(Shader_Type == 0 and ShaderItem.material_model_option == 5): #H3Category: material_model - glass
                    ShaderOutputCount = ShaderOutputCount + 1
                elif(Shader_Type == 0 and ShaderItem.material_model_option == 6): #H3Category: material_model - organism                          USING COOK_TORRANCE FOR NOW FIX LATER
                    ShaderOutputCount = ShaderOutputCount + 1
                elif(Shader_Type == 0 and ShaderItem.material_model_option == 7): #H3Category: material_model - single_lobe_phong
                    ShaderOutputCount = ShaderOutputCount + 1
                elif(Shader_Type == 0 and ShaderItem.material_model_option == 9): #H3Category: material_model - cook_torrance_custom_cube
                    ShaderOutputCount = ShaderOutputCount + 1
                elif(Shader_Type == 0 and ShaderItem.material_model_option == 10): #H3Category: material_model - single_lobe_phong
                    ShaderOutputCount = ShaderOutputCount + 1
                 

                            ######################################################################################
                            #create Add Shader Node or Shader3Group depending on how many Shader Outputs there are
                            ######################################################################################
                #print("Count of Shader Outputs: " + str(ShaderOutputCount))
                
                # .shader files
                if(Shader_Type == 0 and ShaderOutputCount <= 2): #if only less than 1 or 2
                    pymat_copy.node_tree.nodes.new('ShaderNodeAddShader')
                    AddShader = pymat_copy.node_tree.nodes.get("Add Shader")
                elif (Shader_Type == 0 and ShaderOutputCount == 3): #if there are 3
                    Add3Group = instantiate_group(pymat_copy.node_tree.nodes, "H3Utility: Add 3 Shader")
                else:
                    print ("ShaderOutputCount Issue!")
                    
                    
                # .shader_terrain files
                if(Shader_Type == 1 and ShaderOutputCount <= 2): #if only less than 1 or 2 Shader outputs
                    pymat_copy.node_tree.nodes.new('ShaderNodeAddShader')
                    AddShader = pymat_copy.node_tree.nodes.get("Add Shader")
                # elif (Shader_Type == 1 and ShaderOutputCount == 3): #if there are 3
                    # Add3Group = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: Add 3 Shader")
                # elif (Shader_Type == 1 and ShaderOutputCount == 4): #if there are 4
                    # Add4Group = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: Add 4 Shader")   
                # elif (Shader_Type == 1 and ShaderOutputCount == 5): #if there are 5
                    # Add5Group = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: Add 5 Shader")    

                #foliage shader
                if(ShaderItem == 2):
                    #print("  making add shader")
                    pymat_copy.node_tree.nodes.new('ShaderNodeAddShader')
                    AddShader = pymat_copy.node_tree.nodes.get("Add Shader")

                #locations of group
                if(ShaderOutputCount <= 2 or Shader_Type == 2):
                    AddShader.location.x = last_node_x - ADD_SHADER_HORIZONTAL_SPACING
                    AddShader.location.y = last_node_y
                        
                    last_node_x = AddShader.location.x
                    last_node_y = AddShader.location.y

                    end_group_x = AddShader.location.x
                    end_group_y = AddShader.location.y        
                elif(ShaderOutputCount == 3):
                    Add3Group.location.x = last_node_x - ADD_SHADER_HORIZONTAL_SPACING
                    Add3Group.location.y = last_node_y
                        
                    last_node_x = Add3Group.location.x
                    last_node_y = Add3Group.location.y 
                    
                    end_group_x = Add3Group.location.x
                    end_group_y = Add3Group.location.y
                    
                                    #############################
                                    #environment map group create
                                    #############################
                ###############
                # .shader files
                ###############
                
                if(Shader_Type == 0 and ShaderItem.environment_mapping_option == 1): #H3Category: environment_mapping - per_pixel
                    EnvGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: environment_mapping - per_pixel")
                    EnvGroup = apply_group_values(EnvGroup, ShaderItem, "env map")
                    #ShaderOutputCount = ShaderOutputCount + 1
                    ShaderGroupList.append("environment")
                    
                    EnvGroup.location.x = last_node_x
                    EnvGroup.location.y = last_node_y - ENVIRONMENT_GROUP_VERTICAL_SPACING
                        
                    last_node_x = EnvGroup.location.x
                    last_node_y = EnvGroup.location.y 
                elif(Shader_Type == 0 and ShaderItem.environment_mapping_option == 2): #H3Category: environment_mapping - dynamic
                    EnvGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: environment_mapping - dynamic")
                    EnvGroup = apply_group_values(EnvGroup, ShaderItem, "env map")
                    #ShaderOutputCount = ShaderOutputCount + 1
                    ShaderGroupList.append("environment")

                    EnvGroup.location.x = last_node_x
                    EnvGroup.location.y = last_node_y - ENVIRONMENT_GROUP_VERTICAL_SPACING
                        
                    last_node_x = EnvGroup.location.x
                    last_node_y = EnvGroup.location.y 

                                    ########################
                                    #self illum group create
                                    ########################
                ###############
                # .shader files
                ###############
                
                if((Shader_Type == 0 or Shader_Type == 3) and ShaderItem.self_illumination_option == 1): #H3Category: self_illumination - simple
                    SelfIllumGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: self_illumination - simple")
                    SelfIllumGroup = apply_group_values(SelfIllumGroup, ShaderItem, "self illum")
                    #ShaderOutputCount = ShaderOutputCount + 1
                    ShaderGroupList.append("self_illum")
                    illum_group_made = 1
                elif((Shader_Type == 0 or Shader_Type == 3) and ShaderItem.self_illumination_option == 2): #H3Category: self_illumination - 3_channel_self_illum
                    SelfIllumGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: self_illumination - 3_channel_self_illum")
                    SelfIllumGroup = apply_group_values(SelfIllumGroup, ShaderItem, "self illum")
                    #ShaderOutputCount = ShaderOutputCount + 1
                    ShaderGroupList.append("self_illum")
                    illum_group_made = 1
                elif((Shader_Type == 0 or Shader_Type == 3) and ShaderItem.self_illumination_option == 3): #H3Category: self_illumination - plasma
                    SelfIllumGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: self_illumination - plasma")
                    SelfIllumGroup = apply_group_values(SelfIllumGroup, ShaderItem, "self illum")
                    #ShaderOutputCount = ShaderOutputCount + 1
                    ShaderGroupList.append("self_illum")
                    illum_group_made = 1
                elif((Shader_Type == 0 or Shader_Type == 3) and ShaderItem.self_illumination_option == 4): #H3Category: self_illumination - from_diffuse
                    SelfIllumGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: self_illumination - from_diffuse")
                    SelfIllumGroup = apply_group_values(SelfIllumGroup, ShaderItem, "self illum")
                    #ShaderOutputCount = ShaderOutputCount + 1
                    ShaderGroupList.append("self_illum")
                    illum_group_made = 1
                elif((Shader_Type == 0 or Shader_Type == 3) and ShaderItem.self_illumination_option == 5): #H3Category: self_illumination - illum_detail
                    SelfIllumGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: self_illumination - illum_detail")
                    SelfIllumGroup = apply_group_values(SelfIllumGroup, ShaderItem, "self illum")
                    #ShaderOutputCount = ShaderOutputCount + 1
                    ShaderGroupList.append("self_illum")
                    illum_group_made = 1
                elif((Shader_Type == 0 or Shader_Type == 3) and ShaderItem.self_illumination_option == 6): #H3Category: self_illumination - meter
                    SelfIllumGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: self_illumination - meter")
                    SelfIllumGroup = apply_group_values(SelfIllumGroup, ShaderItem, "self illum")
                    #ShaderOutputCount = ShaderOutputCount + 1
                    ShaderGroupList.append("self_illum")
                    illum_group_made = 1
                elif((Shader_Type == 0 or Shader_Type == 3) and ShaderItem.self_illumination_option == 7): #H3Category: self_illumination - self_illum_times_diffuse
                    SelfIllumGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: self_illumination - self_illum_times_diffuse")
                    SelfIllumGroup = apply_group_values(SelfIllumGroup, ShaderItem, "self illum")
                    #ShaderOutputCount = ShaderOutputCount + 1
                    ShaderGroupList.append("self_illum")
                    illum_group_made = 1


                ########################
                # .shader_halogram files
                ########################
                 
                elif(Shader_Type == 3 and ShaderItem.self_illumination_option == 8): #H3Category: self_illumination - multilayer_additive
                    SelfIllumGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: self_illumination - multilayer_additive")
                    SelfIllumGroup = apply_group_values(SelfIllumGroup, ShaderItem, "self illum")
                    #ShaderOutputCount = ShaderOutputCount + 1
                    ShaderGroupList.append("self_illum")
                    illum_group_made = 1
                elif(Shader_Type == 3 and ShaderItem.self_illumination_option == 9): #H3Category: self_illumination - scope_blur
                    SelfIllumGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: self_illumination - scope_blur")
                    SelfIllumGroup = apply_group_values(SelfIllumGroup, ShaderItem, "self illum")
                    #ShaderOutputCount = ShaderOutputCount + 1
                    ShaderGroupList.append("self_illum")
                    illum_group_made = 1 
                elif(Shader_Type == 3 and ShaderItem.self_illumination_option == 10): #H3Category: self_illumination - ml_add_four_change_color
                    SelfIllumGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: self_illumination - ml_add_four_change_color")
                    SelfIllumGroup = apply_group_values(SelfIllumGroup, ShaderItem, "self illum")
                    #ShaderOutputCount = ShaderOutputCount + 1
                    ShaderGroupList.append("self_illum")
                    illum_group_made = 1   
                elif(Shader_Type == 3 and ShaderItem.self_illumination_option == 11): #H3Category: self_illumination - ml_add_five_change_color
                    SelfIllumGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: self_illumination - ml_add_five_change_color")
                    SelfIllumGroup = apply_group_values(SelfIllumGroup, ShaderItem, "self illum")
                    #ShaderOutputCount = ShaderOutputCount + 1
                    ShaderGroupList.append("self_illum")
                    illum_group_made = 1   
                elif(Shader_Type == 3 and ShaderItem.self_illumination_option == 12): #H3Category: self_illumination - plasma_wide_and_sharp_five_change_color
                    SelfIllumGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: self_illumination - plasma_wide_and_sharp_five_change_color")
                    SelfIllumGroup = apply_group_values(SelfIllumGroup, ShaderItem, "self illum")
                    #ShaderOutputCount = ShaderOutputCount + 1
                    ShaderGroupList.append("self_illum")
                    illum_group_made = 1  
                elif(Shader_Type == 3 and ShaderItem.self_illumination_option == 13): #H3Category: self_illumination - self_illum_holograms
                    SelfIllumGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: self_illumination - self_illum_holograms")
                    SelfIllumGroup = apply_group_values(SelfIllumGroup, ShaderItem, "self illum")
                    #ShaderOutputCount = ShaderOutputCount + 1
                    ShaderGroupList.append("self_illum")
                    illum_group_made = 1 



                #location of node group
                if(illum_group_made == 1):
                    SelfIllumGroup.location.x = last_node_x
                    SelfIllumGroup.location.y = last_node_y - SELF_ILLUM_VERTICAL_SPACING
                        
                    last_node_x = SelfIllumGroup.location.x
                    last_node_y = SelfIllumGroup.location.y         

                                    ############################
                                    #material model group create
                                    ############################
                ###############
                # .shader files
                ###############
                
                if((Shader_Type == 0 or Shader_Type == 2) and ShaderItem.material_model_option == 0): #H3Category: materrial_model - diffuse_only
                    MatModelGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: material_model - diffuse_only")
                    MatModelGroup = apply_group_values(MatModelGroup, ShaderItem, "mat model")
                    #ShaderOutputCount = ShaderOutputCount + 1
                    ShaderGroupList.append("material")
                    mat_group_made = 1
                elif(Shader_Type == 0 and ShaderItem.material_model_option == 1): #H3Category: material_model - cook_torrance
                    MatModelGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: material_model - cook_torrance")
                    MatModelGroup = apply_group_values(MatModelGroup, ShaderItem, "mat model")
                    #ShaderOutputCount = ShaderOutputCount + 1
                    ShaderGroupList.append("material")
                    mat_group_made = 1
                elif(Shader_Type == 0 and ShaderItem.material_model_option == 2): #H3Category: material_model - two_lobe_phong
                    MatModelGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: material_model - two_lobe_phong")
                    MatModelGroup = apply_group_values(MatModelGroup, ShaderItem, "mat model")
                    #ShaderOutputCount = ShaderOutputCount + 1
                    ShaderGroupList.append("material")
                    mat_group_made = 1
                elif(Shader_Type == 0 and ShaderItem.material_model_option == 3): #H3Category: material_model - foliage                           #Using Diffuse Only FOR NOW FIX LATER
                    MatModelGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: material_model - diffuse_only")
                    MatModelGroup = apply_group_values(MatModelGroup, ShaderItem, "mat model")
                    #ShaderOutputCount = ShaderOutputCount + 1
                    ShaderGroupList.append("material") 
                    mat_group_made = 1
                elif(Shader_Type == 0 and ShaderItem.material_model_option == 4): #H3Category: material_model - two_lobe_phong
                    print("Mat Model Option: none")
                elif(Shader_Type == 0 and ShaderItem.material_model_option == 5): #H3Category: material_model - glass
                    MatModelGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: material_model - glass")
                    MatModelGroup = apply_group_values(MatModelGroup, ShaderItem, "mat model")
                    #ShaderOutputCount = ShaderOutputCount + 1
                    ShaderGroupList.append("material")
                    mat_group_made = 1
                elif(Shader_Type == 0 and ShaderItem.material_model_option == 6): #H3Category: material_model - organism                          USING COOK_TORRANCE FOR NOW FIX LATER
                    MatModelGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: material_model - cook_torrance")
                    MatModelGroup = apply_group_values(MatModelGroup, ShaderItem, "mat model")
                    #ShaderOutputCount = ShaderOutputCount + 1
                    ShaderGroupList.append("material")  
                    mat_group_made = 1
                elif(Shader_Type == 0 and ShaderItem.material_model_option == 7): #H3Category: material_model - single_lobe_phong
                    MatModelGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: material_model - single_lobe_phong")
                    MatModelGroup = apply_group_values(MatModelGroup, ShaderItem, "mat model")
                    #ShaderOutputCount = ShaderOutputCount + 1
                    ShaderGroupList.append("material")
                    mat_group_made = 1
                elif(Shader_Type == 0 and ShaderItem.material_model_option == 9): #H3Category: material_model - cook_torrance_custom_cube
                    MatModelGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: material_model - cook_torrance")      #USING COOK_TORRANCE FOR NOW FIX LATER
                    MatModelGroup = apply_group_values(MatModelGroup, ShaderItem, "mat model")
                    #ShaderOutputCount = ShaderOutputCount + 1
                    ShaderGroupList.append("material")
                    mat_group_made = 1
                elif(Shader_Type == 0 and ShaderItem.material_model_option == 10): #H3Category: material_model - single_lobe_phong
                    MatModelGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: material_model - cook_torrance_pbr_maps")
                    MatModelGroup = apply_group_values(MatModelGroup, ShaderItem, "mat model")
                    #ShaderOutputCount = ShaderOutputCount + 1
                    ShaderGroupList.append("material")
                    mat_group_made = 1
                
                #location of node group
                if(mat_group_made == 1):
                    MatModelGroup.location.x = end_group_x - 300
                    MatModelGroup.location.y = end_group_y
                        
                    mat_group_x = MatModelGroup.location.x
                    mat_group_y = MatModelGroup.location.y         

                    last_node_x = MatModelGroup.location.x
                    last_node_y = MatModelGroup.location.y 

            #create variable for each category maybe to correct any misassignment?
                                    ####################
                                    #Albedo group create
                                    ####################
                ##############
                # .shader file
                ##############
                
                if((Shader_Type == 0 or Shader_Type == 3 or Shader_Type == 2) and ShaderItem.albedo_option == 0): #H3Category: albedo - default 
                    AlbedoGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: albedo - default")
                    AlbedoGroup = apply_group_values(AlbedoGroup, ShaderItem, "albedo")
                    ShaderGroupList.append("albedo")
                    ShaderGroupList.append("albedo") #extra option for an additional texture being needed IN the order they get connected
                    albedo_group_made = 1
                elif((Shader_Type == 0 or Shader_Type == 3) and ShaderItem.albedo_option == 1): #H3Category: albedo - detail_blend
                    AlbedoGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: albedo - detail_blend")
                    AlbedoGroup = apply_group_values(AlbedoGroup, ShaderItem, "albedo")
                    ShaderGroupList.append("albedo")
                    ShaderGroupList.append("albedo")
                    albedo_group_made = 1
                elif((Shader_Type == 0 or Shader_Type == 3) and ShaderItem.albedo_option == 2): #H3Category: albedo - constant_color
                    AlbedoGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: albedo - constant_color")
                    AlbedoGroup = apply_group_values(AlbedoGroup, ShaderItem, "albedo")
                    ShaderGroupList.append("albedo")
                    albedo_group_made = 1        
                elif((Shader_Type == 0 or Shader_Type == 3) and ShaderItem.albedo_option == 3): #H3Category: albedo - two_change_color
                    AlbedoGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: albedo - two_change_color")
                    AlbedoGroup = apply_group_values(AlbedoGroup, ShaderItem, "albedo")
                    ShaderGroupList.append("albedo")
                    ShaderGroupList.append("albedo")
                    albedo_group_made = 1
                elif((Shader_Type == 0 or Shader_Type == 3) and ShaderItem.albedo_option == 4): #H3Category: albedo - four_change_color
                    AlbedoGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: albedo - four_change_color")
                    AlbedoGroup = apply_group_values(AlbedoGroup, ShaderItem, "albedo")
                    ShaderGroupList.append("albedo")
                    ShaderGroupList.append("albedo")
                    albedo_group_made = 1
                elif((Shader_Type == 0 or Shader_Type == 3) and ShaderItem.albedo_option == 5): #H3Category: albedo - three_detail_blend
                    AlbedoGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: albedo - three_detail_blend")
                    AlbedoGroup = apply_group_values(AlbedoGroup, ShaderItem, "albedo")
                    ShaderGroupList.append("albedo")
                    ShaderGroupList.append("albedo")
                    albedo_group_made = 1
                elif((Shader_Type == 0 or Shader_Type == 3) and ShaderItem.albedo_option == 6): #H3Category: albedo - two_detail_overlay
                    AlbedoGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: albedo - two_detail_overlay")
                    AlbedoGroup = apply_group_values(AlbedoGroup, ShaderItem, "albedo")
                    ShaderGroupList.append("albedo")
                    ShaderGroupList.append("albedo")
                    albedo_group_made = 1
                elif((Shader_Type == 0 or Shader_Type == 3) and ShaderItem.albedo_option == 7): #H3Category: albedo - two_detail
                    AlbedoGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: albedo - two_detail")
                    AlbedoGroup = apply_group_values(AlbedoGroup, ShaderItem, "albedo")
                    ShaderGroupList.append("albedo")
                    ShaderGroupList.append("albedo")
                    albedo_group_made = 1
                elif((Shader_Type == 0 or Shader_Type == 3) and ShaderItem.albedo_option == 8): #H3Category: albedo - color_mask
                    AlbedoGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: albedo - color_mask")
                    AlbedoGroup = apply_group_values(AlbedoGroup, ShaderItem, "albedo")
                    ShaderGroupList.append("albedo")
                    ShaderGroupList.append("albedo")
                    albedo_group_made = 1
                elif(Shader_Type == 0 and ShaderItem.albedo_option == 17): #H3Category: albedo - custom_cube
                    AlbedoGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: albedo - custom_cube")
                    AlbedoGroup = apply_group_values(AlbedoGroup, ShaderItem, "albedo")
                    ShaderGroupList.append("albedo")
                    albedo_group_made = 1


                #location of node group
                if(albedo_group_made == 1):
                    AlbedoGroup.location.x = last_node_x - 350
                    AlbedoGroup.location.y = last_node_y
                        
                    alb_group_x = AlbedoGroup.location.x
                    alb_group_y = AlbedoGroup.location.y    

                                    ######################
                                    #bump map group create
                                    ######################
                ###############
                # .shader files
                ###############
                
                if(Shader_Type == 0 and ShaderItem.bump_mapping_option == 1): #H3Category: bump_mapping - standard
                    BumpGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: bump_mapping - standard")
                    BumpGroup = apply_group_values(BumpGroup, ShaderItem, "bump")
                    ShaderGroupList.append("bump")
                    bump_group_made = 1
                elif(Shader_Type == 0 and ShaderItem.bump_mapping_option == 2): #H3Category: bump_mapping - detail
                    BumpGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: bump_mapping - detail")
                    BumpGroup = apply_group_values(BumpGroup, ShaderItem, "bump")
                    ShaderGroupList.append("bump")
                    ShaderGroupList.append("bump")
                    bump_group_made = 1
                elif(Shader_Type == 0 and ShaderItem.bump_mapping_option == 3): #H3Category: bump_mapping - detail_masked
                    BumpGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: bump_mapping - detail_masked")
                    BumpGroup = apply_group_values(BumpGroup, ShaderItem, "bump")
                    ShaderGroupList.append("bump")
                    ShaderGroupList.append("bump")
                    bump_group_made = 1
                elif(Shader_Type == 0 and ShaderItem.bump_mapping_option == 4): #H3Category: bump_mapping - detail_plus_detail_masked
                    BumpGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: bump_mapping - detail_plus_detail_masked")
                    BumpGroup = apply_group_values(BumpGroup, ShaderItem, "bump")
                    ShaderGroupList.append("bump")
                    ShaderGroupList.append("bump")
                    bump_group_made = 1
                elif(Shader_Type == 0 and ShaderItem.bump_mapping_option == 5): #H3Category: bump_mapping - detail_unorm
                    BumpGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: bump_mapping - detail")
                    BumpGroup = apply_group_values(BumpGroup, ShaderItem, "bump")
                    ShaderGroupList.append("bump")
                    ShaderGroupList.append("bump")
                    bump_group_made = 1
                   
                
                #location of node group    
                if(bump_group_made == 1):
                    BumpGroup.location.x = alb_group_x
                    BumpGroup.location.y = alb_group_y - 400
                        
                    bump_group_x = BumpGroup.location.x
                    bump_group_y = BumpGroup.location.y        
                    
                    last_node_x = BumpGroup.location.x
                    last_node_y = BumpGroup.location.y        

                    
                    

                

                    
                    

                
                # #CREATE ALPHATEXTURE
                # if(Shader_Type == 0 and ShaderItem.alpha_test_option == 1 or ShaderItem.specular_mask_option == 2)):
                    # try:
                        # AlphaTexture = pymat_copy.node_tree.nodes.new('ShaderNodeTexImage')
                        # AlphaTexture.image = bpy.data.images.load(Export_Root + '/' + ShaderItem.alpha_bitmap_dir + IMAGE_EXTENSION)
                    # except: 
                        # print(ShaderItem.bitmap_list[bitm].type + " texture not found")
                            
                        # #default texture for it
                        # #print(directory + '/' + DEFAULT_BITMAP_DIR + "gray_50_percent" + IMAGE_EXTENSION)


                                        #################################
                                        #TERRAIN ENVIRONMENT GROUP CREATE
                                        #################################
                if(Shader_Type == 1 and ShaderItem.environment_map_option != 0):
                    if(ShaderItem.environment_map_option == 1): #per pixel
                        TerrainEnvGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: environment_mapping - per_pixel")
                        TerrainEnvGroup = apply_group_values(TerrainEnvGroup, ShaderItem, "env map")
                    if(ShaderItem.environment_map_option == 2): #dynamic
                        TerrainEnvGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: environment_mapping - dynamic")
                        TerrainEnvGroup = apply_group_values(TerrainEnvGroup, ShaderItem, "env map")
                    
                    TerrainEnvGroup.location.x = end_group_x
                    TerrainEnvGroup.location.y = end_group_y - 300        
                    
                    
             
                                    ############################
                                    #TERRAIN SHADER GROUP CREATE
                                    ############################
                #################                    
                # .shader_terrain
                #################
                
                if(Shader_Type == 1):
                    TerrainGroup = instantiate_group(pymat_copy.node_tree.nodes, "Halo3Category - Master Terrain Material")
                    TerrainGroup = apply_group_values(TerrainGroup, ShaderItem, "terrain")
                    
                    #location of node groups
                    TerrainGroup.location.x = end_group_x - 300
                    TerrainGroup.location.y = end_group_y  

                    last_node_x = TerrainGroup.location.x
                    last_node_y = TerrainGroup.location.y
                    
                    # if(ShaderItem.material_0_option != 2): #if option for m_0 is not off
                        # if(ShaderItem.material_0_option == 0): #if = diffuse_only 
                            # TerrainGroupM0 = instantiate_group(pymat_copy.node_tree.nodes, "Halo3TerrainCategory - material - diffuse_only")
                            # TerrainGroupM0 = apply_group_values(TerrainGroupM0, ShaderItem, "terrain1_m0")
                            # #print("making diffuse only for m0")
                        # if(ShaderItem.material_0_option == 1): #if = diffuse_plus_specular 
                            # TerrainGroupM0 = instantiate_group(pymat_copy.node_tree.nodes, "Halo3TerrainCategory - material - diffuse_plus_specular")
                            # TerrainGroupM0 = apply_group_values(TerrainGroupM0, ShaderItem, "terrain2_m0")
                            # #print("making diffuse spec for m0")
                        # ShaderOutputCount = ShaderOutputCount + 1
                        # ShaderGroupList.append("m_0")
                        # ShaderGroupList.append("m_0")
                        # ShaderGroupList.append("m_0")
                        # ShaderGroupList.append("m_0")
                    
                    # if(ShaderItem.material_1_option != 2): #if option for m_1 is not off
                        # if(ShaderItem.material_1_option == 0): #if = diffuse_only 
                            # TerrainGroupM1 = instantiate_group(pymat_copy.node_tree.nodes, "Halo3TerrainCategory - material - diffuse_only")
                            # TerrainGroupM1 = apply_group_values(TerrainGroupM1, ShaderItem, "terrain1_m1")
                            # #print("making diffuse only for m1")
                        # if(ShaderItem.material_1_option == 1): #if = diffuse_plus_specular 
                            # TerrainGroupM1 = instantiate_group(pymat_copy.node_tree.nodes, "Halo3TerrainCategory - material - diffuse_plus_specular") 
                            # TerrainGroupM1 = apply_group_values(TerrainGroupM1, ShaderItem, "terrain2_m1")
                            # #print("making diffuse spec for m1")
                        # ShaderOutputCount = ShaderOutputCount + 1
                        # ShaderGroupList.append("m_1")
                        # ShaderGroupList.append("m_1")
                        # ShaderGroupList.append("m_1")
                        # ShaderGroupList.append("m_1")                
                
                    # if(ShaderItem.material_2_option != 2): #if option for m_2 is not off
                        # if(ShaderItem.material_2_option == 0): #if = diffuse_only 
                            # TerrainGroupM2 = instantiate_group(pymat_copy.node_tree.nodes, "Halo3TerrainCategory - material - diffuse_only")
                            # TerrainGroupM2 = apply_group_values(TerrainGroupM2, ShaderItem, "terrain1_m2")
                            # #print("making diffuse only for m2")
                        # if(ShaderItem.material_2_option == 1): #if = diffuse_plus_specular 
                            # TerrainGroupM2 = instantiate_group(pymat_copy.node_tree.nodes, "Halo3TerrainCategory - material - diffuse_plus_specular")     
                            # TerrainGroupM2 = apply_group_values(TerrainGroupM2, ShaderItem, "terrain2_m2")
                            # #print("making diffuse spec for m2")
                        # ShaderOutputCount = ShaderOutputCount + 1
                        # ShaderGroupList.append("m_2")
                        # ShaderGroupList.append("m_2")
                        # ShaderGroupList.append("m_2")
                        # ShaderGroupList.append("m_2")
                        
                    # if(ShaderItem.material_3_option != 0): #if option for m_3 is not off
                        # if(ShaderItem.material_3_option == 1): #if = diffuse_only 
                            # TerrainGroupM3 = instantiate_group(pymat_copy.node_tree.nodes, "Halo3TerrainCategory - material - diffuse_only")
                            # TerrainGroupM3 = apply_group_values(TerrainGroupM3, ShaderItem, "terrain1_m3")
                            # #print("making diffuse only for m3")
                        # if(ShaderItem.material_3_option == 2): #if = diffuse_plus_specular 
                            # TerrainGroupM3 = instantiate_group(pymat_copy.node_tree.nodes, "Halo3TerrainCategory - material - diffuse_plus_specular")   
                            # TerrainGroupM3 = apply_group_values(TerrainGroupM3, ShaderItem, "terrain2_m3")  
                            # #print("making diffuse spec for m3")                
                        # ShaderOutputCount = ShaderOutputCount + 1
                        # ShaderGroupList.append("m_3")
                        # ShaderGroupList.append("m_3")
                        # ShaderGroupList.append("m_3")
                        # ShaderGroupList.append("m_3")    
                
                
                
                                   
                                   
                                   
                                   
                                   
                                                   ##################
                                                   #GROUP CONNECTIONS
                                                   ##################
                ###############
                # .shader files
                ###############
                
                #CONNECT "ALBEDO GROUP" TO "MATERIAL MODEL" GROUP
                if(Shader_Type == 0 and ShaderItem.material_model_option != 0 and ShaderItem.material_model_option != 4 and ShaderItem.material_model_option != 3): #every option but "diffuse_only"
                    pymat_copy.node_tree.links.new(MatModelGroup.inputs["albedo.rgb"], AlbedoGroup.outputs["albedo.rgb"])
                    pymat_copy.node_tree.links.new(MatModelGroup.inputs["albedo.a"], AlbedoGroup.outputs["albedo.a"])
                
                
                
                if(Shader_Type == 0 and (ShaderItem.material_model_option == 0 or ShaderItem.material_model_option == 3)): #if material model is diffuse only
                    pymat_copy.node_tree.links.new(MatModelGroup.inputs["albedo.rgb"], AlbedoGroup.outputs["albedo.rgb"])
             
                if(Shader_Type == 2): #if foliage shader
                    pymat_copy.node_tree.links.new(MatModelGroup.inputs["albedo.rgb"], AlbedoGroup.outputs["albedo.rgb"])

             
                #CONNECT "ALBEDO" GROUP TO "SELF ILLUM" GROUP
                if (Shader_Type == 0 and ShaderItem.self_illumination_option == 7):
                    pymat_copy.node_tree.links.new(SelfIllumGroup.inputs["albedo.rgb"], AlbedoGroup.outputs["albedo.rgb"])
                
                # #CONNECT ALPHA TEXTURE TO ALPHA TEST GROUP
                # if(Shader_Type == 0 and ShaderItem.alpha_test_option == 1 or ShaderItem.specular_mask_option == 2)):
                    # pymat_copy.node_tree.links.new(AlphaTestGroup.inputs["alpha_test_map.a"], AlphaTexture.outputs["Alpha"])
                
                
                #CONNECT "BUMP GROUP" TO "MATERIAL MODEL" GROUP
                if(Shader_Type == 0 and ShaderItem.bump_mapping_option != 0): #as long as bump mapping isn't turned off
                    pymat_copy.node_tree.links.new(MatModelGroup.inputs["Normal"], BumpGroup.outputs["Normal"])
                
                    
                #CONNECT "BUMP GROUP" TO "ENVIRONMENT MODEL" GROUP
                if(Shader_Type == 0 and ShaderItem.bump_mapping_option != 0 and ShaderItem.environment_mapping_option == 2): #when Environment Mapping Option is "dynamic"
                    pymat_copy.node_tree.links.new(EnvGroup.inputs["Normal"], BumpGroup.outputs["Normal"])
                    
                #CONNECT "MATERIAL MODEL" TO "ENVIRONMENT MAP" GROUP
                if(Shader_Type == 0 and ShaderItem.environment_mapping_option != 0 and ShaderItem.material_model_option != 4 and ShaderItem.material_model_option != 0): #as long as environment option is not none or diffuse only
                    pymat_copy.node_tree.links.new(EnvGroup.inputs["specular_reflectance_and_roughness.rgb"], MatModelGroup.outputs["specular_reflectance_and_roughness.rgb"])
                    if(ShaderItem.environment_mapping_option == 2 and (ShaderItem.material_model_option == 1 or ShaderItem.material_model_option == 2 or ShaderItem.material_model_option == 5 or ShaderItem.material_model_option == 7 or ShaderItem.material_model_option == 9 or ShaderItem.material_model_option == 10)): #if environment option is dynamic
                        pymat_copy.node_tree.links.new(EnvGroup.inputs["specular_reflectance_and_roughness.a"], MatModelGroup.outputs["specular_reflectance_and_roughness.a"])
                
                
                #CONNECT END SHADER GROUPS TO "ADD SHADER" NODE
                    #material model group
                #rint("mat option: " + str(ShaderItem.material_model_option))
                if (Shader_Type == 0 and (ShaderItem.material_model_option == 0 or ShaderItem.material_model_option == 1 or ShaderItem.material_model_option == 2 or ShaderItem.material_model_option == 3 or ShaderItem.material_model_option == 5 or ShaderItem.material_model_option == 7 or ShaderItem.material_model_option == 9 or ShaderItem.material_model_option == 10)):
                    #print("0")
                    #print("shaders needed: " + str(ShaderOutputCount))
                    if(ShaderOutputCount <= 2): #if only less than 1 or 2 Shader outputs needed
                        #print("fart")
                        if (ShadersConnected == 0):
                            #print("test a")
                            pymat_copy.node_tree.links.new(AddShader.inputs[0], MatModelGroup.outputs["Shader"])
                            ShadersConnected = ShadersConnected + 1
                        elif (ShadersConnected == 1):
                            #print("test b")
                            pymat_copy.node_tree.links.new(AddShader.inputs[1], MatModelGroup.outputs["Shader"])
                            ShadersConnected = ShadersConnected + 1                
                    elif(ShaderOutputCount == 3): #3 Shader outputs needed
                        if (ShadersConnected == 0):                
                            #print("test c")
                            pymat_copy.node_tree.links.new(Add3Group.inputs[0], MatModelGroup.outputs["Shader"])
                            ShadersConnected = ShadersConnected + 1
                        elif (ShadersConnected == 1): 
                            #print("test d")
                            pymat_copy.node_tree.links.new(Add3Group.inputs[1], MatModelGroup.outputs["Shader"])
                            ShadersConnected = ShadersConnected + 1            
                        elif (ShadersConnected == 2):
                            #print("test e")
                            pymat_copy.node_tree.links.new(Add3Group.inputs[2], MatModelGroup.outputs["Shader"])
                            ShadersConnected = ShadersConnected + 1 
                elif (Shader_Type == 0 and ShaderItem.material_model_option == 4): #if mat model set to "none" - plug albedo group into Add Shader
                    if(ShaderOutputCount <= 2): #if only less than 1 or 2 Shader outputs needed
                        if (ShadersConnected == 0):
                            #print("test f")
                        
                            pymat_copy.node_tree.links.new(AddShader.inputs[0], AlbedoGroup.outputs["albedo.rgb"])
                            ShadersConnected = ShadersConnected + 1
                        elif (ShadersConnected == 1):
                            #print("test g")
                            pymat_copy.node_tree.links.new(AddShader.inputs[1], AlbedoGroup.outputs["albedo.rgb"])
                            ShadersConnected = ShadersConnected + 1                
                    elif(ShaderOutputCount == 3): #3 Shader outputs needed
                        if (ShadersConnected == 0):                
                            #print("test h")
                            pymat_copy.node_tree.links.new(Add3Group.inputs[0], AlbedoGroup.outputs["albedo.rgb"])
                            ShadersConnected = ShadersConnected + 1
                        elif (ShadersConnected == 1): 
                            #print("test pymat_copy")
                            pymat_copy.node_tree.links.new(Add3Group.inputs[1], AlbedoGroup.outputs["albedo.rgb"])
                            ShadersConnected = ShadersConnected + 1            
                        elif (ShadersConnected == 2):
                            #print("test j")
                            pymat_copy.node_tree.links.new(Add3Group.inputs[2], AlbedoGroup.outputs["albedo.rgb"])
                            ShadersConnected = ShadersConnected + 1
                # #foliage shaders
                # elif(Shader_Type == 2):
                    # pymat_copy.node_tree.links.new(AddShader.inputs[0], AlbedoGroup.outputs["albedo.rgb"])
                    # ShadersConnected = ShadersConnected + 1        
                print("Shader Outputs Connected: " + str(ShadersConnected))
                    #evnironment map group
                if (Shader_Type == 0 and ShaderItem.environment_mapping_option == 1 or ShaderItem.environment_mapping_option == 2):
                    if(ShaderOutputCount <= 2): #if only less than 1 or 2 Shader outputs needed
                        if (ShadersConnected == 0):
                            #print("test k")
                            pymat_copy.node_tree.links.new(AddShader.inputs[0], EnvGroup.outputs["Shader"])
                            ShadersConnected = ShadersConnected + 1
                        elif (ShadersConnected == 1):
                            #print("test l")
                            pymat_copy.node_tree.links.new(AddShader.inputs[1], EnvGroup.outputs["Shader"])
                            ShadersConnected = ShadersConnected + 1                
                    elif(ShaderOutputCount == 3): #3 Shader outputs needed
                        if (ShadersConnected == 0):                
                            #print("test m")
                            pymat_copy.node_tree.links.new(Add3Group.inputs[0], EnvGroup.outputs["Shader"])
                            ShadersConnected = ShadersConnected + 1
                        elif (ShadersConnected == 1): 
                            #print("test n")
                            pymat_copy.node_tree.links.new(Add3Group.inputs[1], EnvGroup.outputs["Shader"])
                            ShadersConnected = ShadersConnected + 1            
                        elif (ShadersConnected == 2):
                            #print("test o")
                            pymat_copy.node_tree.links.new(Add3Group.inputs[2], EnvGroup.outputs["Shader"])
                            ShadersConnected = ShadersConnected + 1
                print("Shader Outputs Connected: " + str(ShadersConnected))                
                if (Shader_Type == 0 and ShaderItem.self_illumination_option == 1 or ShaderItem.self_illumination_option == 2 or ShaderItem.self_illumination_option == 3 or ShaderItem.self_illumination_option == 4 or ShaderItem.self_illumination_option == 5 or ShaderItem.self_illumination_option == 6 or ShaderItem.self_illumination_option == 7):                
                    if(ShaderOutputCount <= 2): #if only less than 1 or 2 Shader outputs needed
                        if (ShadersConnected == 0):
                            #print("test p")
                            pymat_copy.node_tree.links.new(AddShader.inputs[0], SelfIllumGroup.outputs[0])
                            ShadersConnected = ShadersConnected + 1
                        elif (ShadersConnected == 1):
                            #print("test q")
                            pymat_copy.node_tree.links.new(AddShader.inputs[1], SelfIllumGroup.outputs[0])
                            ShadersConnected = ShadersConnected + 1                
                    elif(ShaderOutputCount == 3): #3 Shader outputs needed
                        if (ShadersConnected == 0):                
                            # print("test r")
                            pymat_copy.node_tree.links.new(Add3Group.inputs[0], SelfIllumGroup.outputs[0])
                            ShadersConnected = ShadersConnected + 1
                        elif (ShadersConnected == 1): 
                            # print("test s")
                            pymat_copy.node_tree.links.new(Add3Group.inputs[1], SelfIllumGroup.outputs[0])
                            ShadersConnected = ShadersConnected + 1            
                        elif (ShadersConnected == 2):
                            #print("test t")
                            pymat_copy.node_tree.links.new(Add3Group.inputs[2], SelfIllumGroup.outputs[0])
                            ShadersConnected = ShadersConnected + 1   
                print("Shader Outputs Connected: " + str(ShadersConnected))
                #CONNECT ALBEDO.rgb GROUP output TO SELF ILLUM if self illum option is "from_diffuse"

                
                #if alpha test exists then alpha test goes right after last add shader and before the material output
                        
                #IF BLEND MODE = additive then add additional Add Shader node and then plug transparency BSDF into that

                        
                        
                #connect "Add Shader" and/or "Materiol Output" and/or "Additive Group" and/or AlphaBlendGroup
                if ((Shader_Type == 0 or Shader_Type == 3) and ShaderOutputCount <= 2):
                    if (ShaderItem.alpha_test_option == 0): #alpha test = off
                        if (ShaderItem.blend_mode_option == 1):
                            #print("test 1")
                            pymat_copy.node_tree.links.new(AdditiveGroup.inputs["Shader"], AddShader.outputs["Shader"])                
                            pymat_copy.node_tree.links.new(material_output.inputs["Surface"], AdditiveGroup.outputs["Shader"])
                        elif(ShaderItem.blend_mode_option == 3 or ShaderItem.blend_mode_option == 5):
                            #print("test 2")
                            pymat_copy.node_tree.links.new(AlphaBlendGroup.inputs["Shader"], AddShader.outputs["Shader"])
                            pymat_copy.node_tree.links.new(material_output.inputs["Surface"], AlphaBlendGroup.outputs["Shader"])
                        else:
                            #print("test 3")
                            pymat_copy.node_tree.links.new(material_output.inputs["Surface"], AddShader.outputs["Shader"])            
                    elif (ShaderItem.alpha_test_option == 1): #alpha test = simple
                        if(ShaderItem.blend_mode_option == 1):
                            #print("test 4")
                            pymat_copy.node_tree.links.new(AlphaTestGroup.inputs["Shader"], AddShader.outputs["Shader"])             
                            pymat_copy.node_tree.links.new(AdditiveGroup.inputs["Shader"], AlphaTestGroup.outputs["Shader"])                
                            pymat_copy.node_tree.links.new(material_output.inputs["Surface"], AdditiveGroup.outputs["Shader"]) 
                        elif(ShaderItem.blend_mode_option == 3 or ShaderItem.blend_mode_option == 5):
                            #print("test 5")
                            pymat_copy.node_tree.links.new(AlphaTestGroup.inputs["Shader"], AddShader.outputs["Shader"])
                            pymat_copy.node_tree.links.new(AlphaBlendGroup.inputs["Shader"], AlphaTestGroup.outputs["Shader"])
                            pymat_copy.node_tree.links.new(material_output.inputs["Surface"], AlphaBlendGroup.outputs["Shader"])            
                        else:
                            #print("test 6")
                            pymat_copy.node_tree.links.new(material_output.inputs["Surface"], AlphaTestGroup.outputs["Shader"])
                            pymat_copy.node_tree.links.new(AlphaTestGroup.inputs["Shader"], AddShader.outputs["Shader"])
                
                
                if ((Shader_Type == 0 or Shader_Type == 3) and ShaderOutputCount == 3):
                    if (ShaderItem.alpha_test_option == 0): #alpha test = off
                        if (ShaderItem.blend_mode_option == 1):
                            pymat_copy.node_tree.links.new(AdditiveGroup.inputs["Shader"], Add3Group.outputs["Shader"])                
                            pymat_copy.node_tree.links.new(material_output.inputs["Surface"], AdditiveGroup.outputs["Shader"])
                        elif(ShaderItem.blend_mode_option == 3 or ShaderItem.blend_mode_option == 5):
                            pymat_copy.node_tree.links.new(AlphaBlendGroup.inputs["Shader"], Add3Group.outputs["Shader"])
                            pymat_copy.node_tree.links.new(material_output.inputs["Surface"], AlphaBlendGroup.outputs["Shader"])            
                        else:
                            pymat_copy.node_tree.links.new(material_output.inputs["Surface"], Add3Group.outputs["Shader"])            
                    elif (ShaderItem.alpha_test_option == 1): #alpha test = simple
                        if(ShaderItem.blend_mode_option == 1):
                            pymat_copy.node_tree.links.new(AlphaTestGroup.inputs["Shader"], Add3Group.outputs["Shader"])             
                            pymat_copy.node_tree.links.new(AdditiveGroup.inputs["Shader"], AlphaTestGroup.outputs["Shader"])                
                            pymat_copy.node_tree.links.new(material_output.inputs["Surface"], AdditiveGroup.outputs["Shader"]) 
                        elif(ShaderItem.blend_mode_option == 3 or ShaderItem.blend_mode_option == 5):
                            pymat_copy.node_tree.links.new(AlphaBlendGroup.inputs["Shader"], Add3Group.outputs["Shader"])
                            pymat_copy.node_tree.links.new(material_output.inputs["Surface"], AlphaBlendGroup.outputs["Shader"])            
                        else:
                            pymat_copy.node_tree.links.new(material_output.inputs["Surface"], AlphaTestGroup.outputs["Shader"])
                            pymat_copy.node_tree.links.new(AlphaTestGroup.inputs["Shader"], Add3Group.outputs["Shader"])
                      
                #######################      
                # .shader_terrain files      
                #######################
                
                #Add Shader Groups to Material Output
                if(Shader_Type == 1):
                    if(ShaderOutputCount <= 2):
                        pymat_copy.node_tree.links.new(material_output.inputs["Surface"], AddShader.outputs["Shader"])
                    else:
                        #print("Count of Shader Outputs 3: " + str(ShaderOutputCount))
                        print("Shader Output value bigger than expected")
                # elif(Shader_Type == 1 and ShaderOutputCount == 3):          
                    # pymat_copy.node_tree.links.new(material_output.inputs["Surface"], Add3Group.outputs["Shader"])          
                # elif(Shader_Type == 1 and ShaderOutputCount == 4):          
                    # pymat_copy.node_tree.links.new(material_output.inputs["Surface"], Add4Group.outputs["Shader"])           
                # elif(Shader_Type == 1 and ShaderOutputCount == 5):          
                    # pymat_copy.node_tree.links.new(material_output.inputs["Surface"], Add5Group.outputs["Shader"])           
                      
                # #separate Color node to terrain shader groups
                # if(Shader_Type == 1):
                    # if(ShaderItem.material_0_option != 2): #if material_0 is not off
                        # pymat_copy.node_tree.links.new(TerrainGroupM0.inputs["blend_map_channel"], SeparateColorGroup.outputs["Red"]) 
                    # if(ShaderItem.material_1_option != 2): #if material_1 is not off
                        # pymat_copy.node_tree.links.new(TerrainGroupM1.inputs["blend_map_channel"], SeparateColorGroup.outputs["Green"])           
                    # if(ShaderItem.material_2_option != 2): #if material_2 is not off
                        # pymat_copy.node_tree.links.new(TerrainGroupM2.inputs["blend_map_channel"], SeparateColorGroup.outputs["Blue"])           
                      
                #connect Terrain shader groups and environment shader groups to AddShader groups      
                if(Shader_Type == 1):
                    connected_shaders = 0 #helps keep track of what spot on AddShader to plug into
                    
                    if(ShaderOutputCount <= 2): #if there are 2 or less shader outputs needed            
                        pymat_copy.node_tree.links.new(AddShader.inputs[0], TerrainGroup.outputs["Shader"])
                        
                        if (ShaderItem.environment_map_option == 1): # per_pixel
                            #Connect TerrainGroup to TerrainEnvGroup
                            pymat_copy.node_tree.links.new(TerrainEnvGroup.inputs[0], TerrainGroup.outputs[1])
                            
                            #Connect TerrainEvnGroup to AddShader
                            pymat_copy.node_tree.links.new(AddShader.inputs[1], TerrainEnvGroup.outputs[0])
                        elif (ShaderItem.environment_map_option == 2): # dynamic
                            #Connect TerrainGroup to TerrainEnvGroup
                            pymat_copy.node_tree.links.new(TerrainEnvGroup.inputs[0], TerrainGroup.outputs[1])  
                            pymat_copy.node_tree.links.new(TerrainEnvGroup.inputs[1], TerrainGroup.outputs[2])
                            pymat_copy.node_tree.links.new(TerrainEnvGroup.inputs["Normal"], TerrainGroup.outputs["Normal"])
                            
                            #connect TerrainEnvGroup to AddShader
                            pymat_copy.node_tree.links.new(AddShader.inputs[1], TerrainEnvGroup.outputs[0])
                       

                       # if(ShaderItem.material_0_option != 2): #if material_0 is not off
                            # pymat_copy.node_tree.links.new(AddShader.inputs[connected_shaders], TerrainGroupM0.outputs["Shader"]) 
                            # connected_shaders = connected_shaders + 1
                        # if(ShaderItem.material_1_option != 2): #if material_1 is not off
                            # pymat_copy.node_tree.links.new(AddShader.inputs[connected_shaders], TerrainGroupM1.outputs["Shader"]) 
                            # connected_shaders = connected_shaders + 1              
                        # if(ShaderItem.material_2_option != 2): #if material_2 is not off
                            # pymat_copy.node_tree.links.new(AddShader.inputs[connected_shaders], TerrainGroupM2.outputs["Shader"]) 
                            # connected_shaders = connected_shaders + 1    
                        # if(ShaderItem.material_3_option != 0): #if material_3 is not off
                            # pymat_copy.node_tree.links.new(AddShader.inputs[connected_shaders], TerrainGroupM3.outputs["Shader"]) 
                            # connected_shaders = connected_shaders + 1                    

                    # elif(ShaderOutputCount == 3): #if there are 2 or less shader outputs needed            
                        # if(ShaderItem.material_0_option != 2): #if material_0 is not off
                            # pymat_copy.node_tree.links.new(Add3Group.inputs[connected_shaders], TerrainGroupM0.outputs["Shader"]) 
                            # connected_shaders = connected_shaders + 1
                        # if(ShaderItem.material_1_option != 2): #if material_1 is not off
                            # pymat_copy.node_tree.links.new(Add3Group.inputs[connected_shaders], TerrainGroupM1.outputs["Shader"]) 
                            # connected_shaders = connected_shaders + 1              
                        # if(ShaderItem.material_2_option != 2): #if material_2 is not off
                            # pymat_copy.node_tree.links.new(Add3Group.inputs[connected_shaders], TerrainGroupM2.outputs["Shader"]) 
                            # connected_shaders = connected_shaders + 1    
                        # if(ShaderItem.material_3_option != 0): #if material_3 is not off
                            # pymat_copy.node_tree.links.new(Add3Group.inputs[connected_shaders], TerrainGroupM3.outputs["Shader"]) 
                            # connected_shaders = connected_shaders + 1                    

                    # elif(ShaderOutputCount == 4): #if there are 2 or less shader outputs needed            
                        # if(ShaderItem.material_0_option != 2): #if material_0 is not off
                            # pymat_copy.node_tree.links.new(Add4Group.inputs[connected_shaders], TerrainGroupM0.outputs["Shader"]) 
                            # connected_shaders = connected_shaders + 1
                        # if(ShaderItem.material_1_option != 2): #if material_1 is not off
                            # pymat_copy.node_tree.links.new(Add4Group.inputs[connected_shaders], TerrainGroupM1.outputs["Shader"]) 
                            # connected_shaders = connected_shaders + 1              
                        # if(ShaderItem.material_2_option != 2): #if material_2 is not off
                            # pymat_copy.node_tree.links.new(Add4Group.inputs[connected_shaders], TerrainGroupM2.outputs["Shader"]) 
                            # connected_shaders = connected_shaders + 1    
                        # if(ShaderItem.material_3_option != 0): #if material_3 is not off
                            # pymat_copy.node_tree.links.new(Add4Group.inputs[connected_shaders], TerrainGroupM3.outputs["Shader"]) 
                            # connected_shaders = connected_shaders + 1 

                    # elif(ShaderOutputCount == 5): #if there are 2 or less shader outputs needed            
                        # if(ShaderItem.material_0_option != 2): #if material_0 is not off
                            # pymat_copy.node_tree.links.new(Add5Group.inputs[connected_shaders], TerrainGroupM0.outputs["Shader"]) 
                            # connected_shaders = connected_shaders + 1
                        # if(ShaderItem.material_1_option != 2): #if material_1 is not off
                            # pymat_copy.node_tree.links.new(Add5Group.inputs[connected_shaders], TerrainGroupM1.outputs["Shader"]) 
                            # connected_shaders = connected_shaders + 1              
                        # if(ShaderItem.material_2_option != 2): #if material_2 is not off
                            # pymat_copy.node_tree.links.new(Add5Group.inputs[connected_shaders], TerrainGroupM2.outputs["Shader"]) 
                            # connected_shaders = connected_shaders + 1    
                        # if(ShaderItem.material_3_option != 0): #if material_3 is not off
                            # pymat_copy.node_tree.links.new(Add5Group.inputs[connected_shaders], TerrainGroupM3.outputs["Shader"]) 
                            # connected_shaders = connected_shaders + 1       

             

                #######################      
                # .shader_foliage files      
                #######################

                if(Shader_Type == 2):
                    if (ShaderItem.alpha_test_option != 0):
                        print("      foliage 1")
                        pymat_copy.node_tree.links.new(material_output.inputs["Surface"], AlphaTestGroup.outputs["Shader"])
                        pymat_copy.node_tree.links.new(AlphaTestGroup.inputs["Shader"], MatModelGroup.outputs["Shader"])
                    else:
                        pymat_copy.node_tree.links.new(material_output.inputs["Surface"], MatModelGroup.outputs["Shader"])
                        print("      foliage 2")


                #######################      
                # .shader_halogram files      
                #######################

                



















                #prep the area for textures
                last_texture_x = alb_group_x - TEXTURE_NODE_HORIZONTAL_PLACEMENT
                last_texture_y = alb_group_y + TEXTURE_NODE_VERTICAL_PLACEMENT
                MIRROR_PADDING = 0



                #fix texture location for terrain files
                if (Shader_Type == 1):
                    last_texture_x = last_texture_x - 400




                                    ####################################
                                    #CREATE TEXTURE NODES AND OTHER DATA  
                                    ####################################   
                #loop through all bitmaps and create new image texture nodes for each one and scaling nodes        
                for bitm in range(ShaderItem.bitmap_count): 
                 
                 
                    #adjust location     
                    last_texture_x = last_texture_x
                    last_texture_y = last_texture_y - TEXTURE_GROUP_VERTICAL_SPACING - MIRROR_PADDING
                
                    #fix texture start position if it is too high up
                    if(last_texture_y > 400):
                        last_texture_y = 100
                
                
                    #correct texture node placement when there is no texture made
                    before_no_tex_x = last_texture_x
                    before_no_tex_y = last_texture_y
                    
                    print("last_texture_x: " + str(last_texture_x))
                    print("last_texture_y: " + str(last_texture_y))
                    
                    gamma_node_made = 0
                    texture_node_made = 0
                    mirror_node_made = 0
                    trans_node_made = 0
                 
                    #mapping and scaling node with values
                    #image texture node
                    #connect the nodes together
                    #TexImage.bl_idname = "TexImage" + str(bitm)
                    #print("bitm: " + str(bitm))
                    #print(ShaderItem.bitmap_list[bitm].type)
                    #DO A TRY BLOCK HERE IN CASE A TEXTURE CANNOT BE FOUND!!!!!!!!!!!

                    #CREATE NEEDED TEXTURE NODES
                    ImageTextureNodeList.append(pymat_copy.node_tree.nodes.new('ShaderNodeTexImage')) #add image texture for each bitmap needed
                    bitmap_error = 0

                    #Create Textures IF the option for them are not turned off
                    if (Is_Bitmap_Disabled(ShaderItem, ShaderItem.bitmap_list[bitm].type) != True):
                        print(ShaderItem.bitmap_list[bitm].type + " is not disabled")
                        #print(ImageTextureNodeList)
                        

                        
                        
                        if (is_valid_dir(ShaderItem.bitmap_list[bitm].directory) == True):    
                            filepath = bpy.data.filepath
                            directory = os.path.dirname(filepath)
                            
                            if (directory == "" or directory == " " or directory == "  "):
                                directory = Export_Root
                            
                            try:
                                #CUBEMAP CONVERSION CODE TESTING
                                #if (ShaderItem.bitmap_list[bitm].type == "environment_map"):
                                    #convert texture to equirectangular map
                                    #os.system("python convert_cube.py " + ShaderItem.bitmap_list[bitm].directory + IMAGE_EXTENSION + " " + IMAGE_EXTENSION)
                                #else:
                                ImageTextureNodeList[bitm + 1].image = bpy.data.images.load(directory + '/' + ShaderItem.bitmap_list[bitm].directory + IMAGE_EXTENSION)
                                print("Created type: " + ShaderItem.bitmap_list[bitm].type)
                                texture_node_made = 1
                            except: 
                                print(ShaderItem.bitmap_list[bitm].type + " texture not found")
                                    
                                #if statements for default_detail and gray_50_percent
                                if (uses_gray_50(ShaderItem.bitmap_list[bitm].type) == True):
                                    print(directory + '/' + DEFAULT_BITMAP_DIR + "gray_50_percent" + IMAGE_EXTENSION)
                                    ImageTextureNodeList[bitm + 1].image = bpy.data.images.load(directory + '/' + DEFAULT_BITMAP_DIR + "gray_50_percent" + IMAGE_EXTENSION)
                                    print("gray_50_percent has been added to" + ShaderItem.bitmap_list[bitm].type)
                                    #BE SURE TO ADD IN DEFAULT DATA AS WELL LATER
                                    texture_node_made = 1
                                elif (uses_default_detail(ShaderItem.bitmap_list[bitm].type) == True):
                                    ImageTextureNodeList[bitm + 1].image = bpy.data.images.load(directory + '/' + DEFAULT_BITMAP_DIR + "default_detail" + IMAGE_EXTENSION)
                                    print("default detail has been added to " + ShaderItem.bitmap_list[bitm].type)
                                    #BE SURE TO ADD IN DEFAULT DATA AS WELL LATER
                                    texture_node_made = 1
                                elif (uses_default_vector(ShaderItem.bitmap_list[bitm].type) == True):
                                    ImageTextureNodeList[bitm + 1].image = bpy.data.images.load(directory + '/' + DEFAULT_BITMAP_DIR + "default_vector" + IMAGE_EXTENSION)
                                    print("default vector has been added to " + ShaderItem.bitmap_list[bitm].type)
                                    #BE SURE TO ADD IN DEFAULT DATA AS WELL LATER
                                    texture_node_made = 1
                                else:
                                    bitmap_error = 1
                                    print("NoneType Created for: " + ShaderItem.bitmap_list[bitm].type)
                            
                            
                            # #Specular data linking to main group shaders
                            # if(bitmap_error != 1 and (ShaderItem.specular_mask_option == 1)):
                                # print(ShaderItem.bitmap_list[bitm].type + " Image has alpha data")
                            # elif (bitmap_error != 1 and ShaderItem.specular_mask_option == 0):
                                # print("No Specular")
                            # else:
                                # print("Possible specular data")
                            
                            #Edit the names of the created Image Texture nodes
                            try:
                                ImageTextureNodeList[bitm + 1].image.name =  "[" + ShaderItem.bitmap_list[bitm].type + "]  " + ImageTextureNodeList[bitm + 1].image.name
                                print(ImageTextureNodeList[bitm + 1].name)
                            except:
                                print("Couldn't rename NoneType!")
                            
                                
                                                ###################
                                                #CREATE GAMMA NODES
                                                ###################
                            #Handle Curve/Colorspace Data
                            
                            if(ShaderItem.bitmap_list[bitm].curve_option == 0 and bitmap_error != 1): #curve = unknown  CHECK WITH CHIEF
                                ImageTextureNodeList[bitm + 1].image.colorspace_settings.name = "Linear"                    
                            elif(ShaderItem.bitmap_list[bitm].curve_option == 1 and bitmap_error != 1): #curve = xRGB
                                ImageTextureNodeList[bitm + 1].image.colorspace_settings.name = "Linear"
                                gamma_value = 1.95
                                gamma_node_made = 1
                                # .shader files
                                if(ShaderItem.bitmap_list[bitm].type == "base_map"):
                                    #create Gamma Node
                                    GammaNode_Base = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
                                    GammaNode_Base.inputs.get("Gamma").default_value = gamma_value

                                    #link Gamma Node
                                    pymat_copy.node_tree.links.new(GammaNode_Base.inputs["Color"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                
                                    GammaNode_Base.location.x = last_texture_x + TEXTURE_GAMMA_HORIZONTAL_PLACEMENT
                                    GammaNode_Base.location.y = last_texture_y
                                    GammaNode_Base.hide = True
                                elif(ShaderItem.bitmap_list[bitm].type == "detail_map"):
                                    #create Gamma Node
                                    GammaNode_Detail = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
                                    GammaNode_Detail.inputs.get("Gamma").default_value = gamma_value

                                    #link Gamma Node
                                    pymat_copy.node_tree.links.new(GammaNode_Detail.inputs["Color"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                
                                    GammaNode_Detail.location.x = last_texture_x + TEXTURE_GAMMA_HORIZONTAL_PLACEMENT
                                    GammaNode_Detail.location.y = last_texture_y
                                    GammaNode_Detail.hide = True    
                                elif(ShaderItem.bitmap_list[bitm].type == "detail_map2"):
                                    #create Gamma Node
                                    GammaNode_Detail = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
                                    GammaNode_Detail.inputs.get("Gamma").default_value = gamma_value

                                    #link Gamma Node
                                    pymat_copy.node_tree.links.new(GammaNode_Detail.inputs["Color"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                
                                    GammaNode_Detail.location.x = last_texture_x + TEXTURE_GAMMA_HORIZONTAL_PLACEMENT
                                    GammaNode_Detail.location.y = last_texture_y
                                    GammaNode_Detail.hide = True  
                                elif(ShaderItem.bitmap_list[bitm].type == "detail_map3"):
                                    #create Gamma Node
                                    GammaNode_Detail = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
                                    GammaNode_Detail.inputs.get("Gamma").default_value = gamma_value

                                    #link Gamma Node
                                    pymat_copy.node_tree.links.new(GammaNode_Detail.inputs["Color"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                
                                    GammaNode_Detail.location.x = last_texture_x + TEXTURE_GAMMA_HORIZONTAL_PLACEMENT
                                    GammaNode_Detail.location.y = last_texture_y
                                    GammaNode_Detail.hide = True                                      
                                elif(ShaderItem.bitmap_list[bitm].type == "bump_map"):
                                    #create Gamma Node
                                    GammaNode_Bump = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
                                    GammaNode_Bump.inputs.get("Gamma").default_value = gamma_value

                                    #link Gamma Node
                                    pymat_copy.node_tree.links.new(GammaNode_Bump.inputs["Color"], ImageTextureNodeList[bitm + 1].outputs["Color"])

                                    GammaNode_Bump.location.x = last_texture_x + TEXTURE_GAMMA_HORIZONTAL_PLACEMENT
                                    GammaNode_Bump.location.y = last_texture_y                     
                                    GammaNode_Bump.hide = True
                                elif(ShaderItem.bitmap_list[bitm].type == "bump_detail_map"):
                                    #create Gamma Node
                                    GammaNode_BumpDetail = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
                                    GammaNode_BumpDetail.inputs.get("Gamma").default_value = gamma_value

                                    #link Gamma Node
                                    pymat_copy.node_tree.links.new(GammaNode_BumpDetail.inputs["Color"], ImageTextureNodeList[bitm + 1].outputs["Color"])
             
                                    GammaNode_BumpDetail.location.x = last_texture_x + TEXTURE_GAMMA_HORIZONTAL_PLACEMENT
                                    GammaNode_BumpDetail.location.y = last_texture_y 
                                    GammaNode_BumpDetail.hide = True
                                elif(ShaderItem.bitmap_list[bitm].type == "self_illum_map"):
                                    #create Gamma Node
                                    GammaNode_SelfIllum = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
                                    GammaNode_SelfIllum.inputs.get("Gamma").default_value = gamma_value

                                    #link Gamma Node
                                    pymat_copy.node_tree.links.new(GammaNode_SelfIllum.inputs["Color"], ImageTextureNodeList[bitm + 1].outputs["Color"])

                                    GammaNode_SelfIllum.location.x = last_texture_x + TEXTURE_GAMMA_HORIZONTAL_PLACEMENT
                                    GammaNode_SelfIllum.location.y = last_texture_y 
                                    GammaNode_SelfIllum.hide = True
                                elif(ShaderItem.bitmap_list[bitm].type == "self_illum_detail_map"):
                                    #create Gamma Node
                                    GammaNode_SelfIllumDetail = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
                                    GammaNode_SelfIllumDetail.inputs.get("Gamma").default_value = gamma_value

                                    #link Gamma Node
                                    pymat_copy.node_tree.links.new(GammaNode_SelfIllumDetail.inputs["Color"], ImageTextureNodeList[bitm + 1].outputs["Color"])
             
                                    GammaNode_SelfIllumDetail.location.x = last_texture_x + TEXTURE_GAMMA_HORIZONTAL_PLACEMENT
                                    GammaNode_SelfIllumDetail.location.y = last_texture_y  
                                    GammaNode_SelfIllumDetail.hide = True
                                #TERRAIN BITMAPS
                                elif(ShaderItem.bitmap_list[bitm].type == "base_map_m_0"):
                                    #create Gamma Node
                                    GammaNode_Base_M0 = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
                                    GammaNode_Base_M0.inputs.get("Gamma").default_value = gamma_value

                                    #link Gamma Node
                                    pymat_copy.node_tree.links.new(GammaNode_Base_M0.inputs["Color"], ImageTextureNodeList[bitm + 1].outputs["Color"])

                                    GammaNode_Base_M0.location.x = last_texture_x + TEXTURE_GAMMA_HORIZONTAL_PLACEMENT
                                    GammaNode_Base_M0.location.y = last_texture_y                    
                                    GammaNode_Base_M0.hide = True
                                elif(ShaderItem.bitmap_list[bitm].type == "base_map_m_1"):
                                    #create Gamma Node
                                    GammaNode_Base_M1 = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
                                    GammaNode_Base_M1.inputs.get("Gamma").default_value = gamma_value

                                    #link Gamma Node
                                    pymat_copy.node_tree.links.new(GammaNode_Base_M1.inputs["Color"], ImageTextureNodeList[bitm + 1].outputs["Color"])
             
                                    GammaNode_Base_M1.location.x = last_texture_x + TEXTURE_GAMMA_HORIZONTAL_PLACEMENT
                                    GammaNode_Base_M1.location.y = last_texture_y  
                                    GammaNode_Base_M1.hide = True
                                elif(ShaderItem.bitmap_list[bitm].type == "base_map_m_2"):
                                    #create Gamma Node
                                    GammaNode_Base_M2 = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
                                    GammaNode_Base_M2.inputs.get("Gamma").default_value = gamma_value

                                    #link Gamma Node
                                    pymat_copy.node_tree.links.new(GammaNode_Base_M2.inputs["Color"], ImageTextureNodeList[bitm + 1].outputs["Color"])

                                    GammaNode_Base_M2.location.x = last_texture_x + TEXTURE_GAMMA_HORIZONTAL_PLACEMENT
                                    GammaNode_Base_M2.location.y = last_texture_y 
                                    GammaNode_Base_M2.hide = True
                                elif(ShaderItem.bitmap_list[bitm].type == "base_map_m_3"):
                                    #create Gamma Node
                                    GammaNode_Base_M3 = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
                                    GammaNode_Base_M3.inputs.get("Gamma").default_value = gamma_value

                                    #link Gamma Node
                                    pymat_copy.node_tree.links.new(GammaNode_Base_M3.inputs["Color"], ImageTextureNodeList[bitm + 1].outputs["Color"])   

                                    GammaNode_Base_M3.location.x = last_texture_x + TEXTURE_GAMMA_HORIZONTAL_PLACEMENT
                                    GammaNode_Base_M3.location.y = last_texture_y                    
                                    GammaNode_Base_M3.hide = True
                                elif(ShaderItem.bitmap_list[bitm].type == "detail_map_m_0"):
                                    #create Gamma Node
                                    GammaNode_Detail_M0 = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
                                    GammaNode_Detail_M0.inputs.get("Gamma").default_value = gamma_value

                                    #link Gamma Node
                                    pymat_copy.node_tree.links.new(GammaNode_Detail_M0.inputs["Color"], ImageTextureNodeList[bitm + 1].outputs["Color"])                     

                                    GammaNode_Detail_M0.location.x = last_texture_x + TEXTURE_GAMMA_HORIZONTAL_PLACEMENT
                                    GammaNode_Detail_M0.location.y = last_texture_y 
                                    GammaNode_Detail_M0.hide = True
                                elif(ShaderItem.bitmap_list[bitm].type == "detail_map_m_1"):
                                    #create Gamma Node
                                    GammaNode_Detail_M1 = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
                                    GammaNode_Detail_M1.inputs.get("Gamma").default_value = gamma_value

                                    #link Gamma Node
                                    pymat_copy.node_tree.links.new(GammaNode_Detail_M1.inputs["Color"], ImageTextureNodeList[bitm + 1].outputs["Color"])  

                                    GammaNode_Detail_M1.location.x = last_texture_x + TEXTURE_GAMMA_HORIZONTAL_PLACEMENT
                                    GammaNode_Detail_M1.location.y = last_texture_y                         
                                    GammaNode_Detail_M1.hide = True
                                elif(ShaderItem.bitmap_list[bitm].type == "detail_map_m_2"):
                                    #create Gamma Node
                                    GammaNode_Detail_M2 = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
                                    GammaNode_Detail_M2.inputs.get("Gamma").default_value = gamma_value

                                    #link Gamma Node
                                    pymat_copy.node_tree.links.new(GammaNode_Detail_M2.inputs["Color"], ImageTextureNodeList[bitm + 1].outputs["Color"])  

                                    GammaNode_Detail_M2.location.x = last_texture_x + TEXTURE_GAMMA_HORIZONTAL_PLACEMENT
                                    GammaNode_Detail_M2.location.y = last_texture_y 
                                    GammaNode_Detail_M2.hide = True
                                elif(ShaderItem.bitmap_list[bitm].type == "detail_map_m_3"):
                                    #create Gamma Node
                                    GammaNode_Detail_M3 = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
                                    GammaNode_Detail_M3.inputs.get("Gamma").default_value = gamma_value

                                    #link Gamma Node
                                    pymat_copy.node_tree.links.new(GammaNode_Detail_M3.inputs["Color"], ImageTextureNodeList[bitm + 1].outputs["Color"])                          

                                    GammaNode_Detail_M3.location.x = last_texture_x + TEXTURE_GAMMA_HORIZONTAL_PLACEMENT
                                    GammaNode_Detail_M3.location.y = last_texture_y                     
                                    GammaNode_Detail_M3.hide = True
                                elif(ShaderItem.bitmap_list[bitm].type == "bump_map_m_0"):
                                    #create Gamma Node
                                    GammaNode_Bump_M0 = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
                                    GammaNode_Bump_M0.inputs.get("Gamma").default_value = gamma_value

                                    #link Gamma Node
                                    pymat_copy.node_tree.links.new(GammaNode_Bump_M0.inputs["Color"], ImageTextureNodeList[bitm + 1].outputs["Color"])                      

                                    GammaNode_Bump_M0.location.x = last_texture_x + TEXTURE_GAMMA_HORIZONTAL_PLACEMENT
                                    GammaNode_Bump_M0.location.y = last_texture_y  
                                    GammaNode_Bump_M0.hide = True
                                elif(ShaderItem.bitmap_list[bitm].type == "bump_map_m_1"):
                                    #create Gamma Node
                                    GammaNode_Bump_M1 = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
                                    GammaNode_Bump_M1.inputs.get("Gamma").default_value = gamma_value

                                    #link Gamma Node
                                    pymat_copy.node_tree.links.new(GammaNode_Bump_M1.inputs["Color"], ImageTextureNodeList[bitm + 1].outputs["Color"])  

                                    GammaNode_Bump_M1.location.x = last_texture_x + TEXTURE_GAMMA_HORIZONTAL_PLACEMENT
                                    GammaNode_Bump_M1.location.y = last_texture_y 
                                    GammaNode_Bump_M1.hide = True
                                elif(ShaderItem.bitmap_list[bitm].type == "bump_map_m_2"):
                                    #create Gamma Node
                                    GammaNode_Bump_M2 = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
                                    GammaNode_Bump_M2.inputs.get("Gamma").default_value = gamma_value

                                    #link Gamma Node
                                    pymat_copy.node_tree.links.new(GammaNode_Bump_M2.inputs["Color"], ImageTextureNodeList[bitm + 1].outputs["Color"])  

                                    GammaNode_Bump_M2.location.x = last_texture_x + TEXTURE_GAMMA_HORIZONTAL_PLACEMENT
                                    GammaNode_Bump_M2.location.y = last_texture_y 
                                    GammaNode_Bump_M2.hide = True
                                elif(ShaderItem.bitmap_list[bitm].type == "bump_map_m_3"):
                                    #create Gamma Node
                                    GammaNode_Bump_M3 = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
                                    GammaNode_Bump_M3.inputs.get("Gamma").default_value = gamma_value

                                    #link Gamma Node
                                    pymat_copy.node_tree.links.new(GammaNode_Bump_M3.inputs["Color"], ImageTextureNodeList[bitm + 1].outputs["Color"])

                                    GammaNode_Bump_M3.location.x = last_texture_x + TEXTURE_GAMMA_HORIZONTAL_PLACEMENT
                                    GammaNode_Bump_M3.location.y = last_texture_y 
                                    GammaNode_Bump_M3.hide = True
                                elif(ShaderItem.bitmap_list[bitm].type == "detail_bump_m_0"):
                                    #create Gamma Node
                                    GammaNode_Detail_Bump_M0 = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
                                    GammaNode_Detail_Bump_M0.inputs.get("Gamma").default_value = gamma_value

                                    #link Gamma Node
                                    pymat_copy.node_tree.links.new(GammaNode_Detail_Bump_M0.inputs["Color"], ImageTextureNodeList[bitm + 1].outputs["Color"])  

                                    GammaNode_Detail_Bump_M0.location.x = last_texture_x + TEXTURE_GAMMA_HORIZONTAL_PLACEMENT
                                    GammaNode_Detail_Bump_M0.location.y = last_texture_y 
                                    GammaNode_Detail_Bump_M0.hide = True
                                elif(ShaderItem.bitmap_list[bitm].type == "detail_bump_m_1"):
                                    #create Gamma Node
                                    GammaNode_Detail_Bump_M1 = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
                                    GammaNode_Detail_Bump_M1.inputs.get("Gamma").default_value = gamma_value

                                    #link Gamma Node
                                    pymat_copy.node_tree.links.new(GammaNode_Detail_Bump_M1.inputs["Color"], ImageTextureNodeList[bitm + 1].outputs["Color"]) 

                                    GammaNode_Detail_Bump_M1.location.x = last_texture_x + TEXTURE_GAMMA_HORIZONTAL_PLACEMENT
                                    GammaNode_Detail_Bump_M1.location.y = last_texture_y 
                                    GammaNode_Detail_Bump_M1.hide = True
                                elif(ShaderItem.bitmap_list[bitm].type == "detail_bump_m_2"):
                                    #create Gamma Node
                                    GammaNode_Detail_Bump_M2 = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
                                    GammaNode_Detail_Bump_M2.inputs.get("Gamma").default_value = gamma_value

                                    #link Gamma Node
                                    pymat_copy.node_tree.links.new(GammaNode_Detail_Bump_M2.inputs["Color"], ImageTextureNodeList[bitm + 1].outputs["Color"]) 

                                    GammaNode_Detail_Bump_M2.location.x = last_texture_x + TEXTURE_GAMMA_HORIZONTAL_PLACEMENT
                                    GammaNode_Detail_Bump_M2.location.y = last_texture_y 
                                    GammaNode_Detail_Bump_M2.hide = True
                                elif(ShaderItem.bitmap_list[bitm].type == "detail_bump_m_3"):
                                    #create Gamma Node
                                    GammaNode_Detail_Bump_M3 = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
                                    GammaNode_Detail_Bump_M3.inputs.get("Gamma").default_value = gamma_value

                                    #link Gamma Node
                                    pymat_copy.node_tree.links.new(GammaNode_Detail_Bump_M3.inputs["Color"], ImageTextureNodeList[bitm + 1].outputs["Color"])                         

                                    GammaNode_Detail_Bump_M3.location.x = last_texture_x + TEXTURE_GAMMA_HORIZONTAL_PLACEMENT
                                    GammaNode_Detail_Bump_M3.location.y = last_texture_y
                                    GammaNode_Detail_Bump_M3.hide = True
                                else:
                                    print("Unhandled texture type trying to be assinged a Gamma Node")
                                #make_gamma(pymat_copy.node_tree, ImageTextureNodeList[bitm + 1], ShaderItem.bitmap_list[bitm].type, 1.95)
                                
                                # #create Gamma Nodes
                                # GammaNode = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
                                # GammaNode.inputs.get("Gamma").default_value = 1.95
                                
                                #link Image Texture to Gamma
                                #pymat_copy.node_tree.links.new(GammaNode.inputs["Color"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                
                            elif(ShaderItem.bitmap_list[bitm].curve_option == 2 and bitmap_error != 1): #curve = gamma 2.0
                                ImageTextureNodeList[bitm + 1].image.colorspace_settings.name = "Linear"
                                gamma_value = 2.00
                                gamma_node_made = 1

                                if(ShaderItem.bitmap_list[bitm].type == "base_map"):
                                    #create Gamma Node
                                    GammaNode_Base = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
                                    GammaNode_Base.inputs.get("Gamma").default_value = gamma_value

                                    #link Gamma Node
                                    pymat_copy.node_tree.links.new(GammaNode_Base.inputs["Color"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                
                                    GammaNode_Base.location.x = last_texture_x + TEXTURE_GAMMA_HORIZONTAL_PLACEMENT
                                    GammaNode_Base.location.y = last_texture_y                     
                                    GammaNode_Base.hide = True
                                elif(ShaderItem.bitmap_list[bitm].type == "detail_map"):
                                    #create Gamma Node
                                    GammaNode_Detail = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
                                    GammaNode_Detail.inputs.get("Gamma").default_value = gamma_value

                                    #link Gamma Node
                                    pymat_copy.node_tree.links.new(GammaNode_Detail.inputs["Color"], ImageTextureNodeList[bitm + 1].outputs["Color"])

                                    GammaNode_Detail.location.x = last_texture_x + TEXTURE_GAMMA_HORIZONTAL_PLACEMENT
                                    GammaNode_Detail.location.y = last_texture_y                     
                                    GammaNode_Detail.hide = True
                                elif(ShaderItem.bitmap_list[bitm].type == "detail_map2"):
                                    #create Gamma Node
                                    GammaNode_Detail = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
                                    GammaNode_Detail.inputs.get("Gamma").default_value = gamma_value

                                    #link Gamma Node
                                    pymat_copy.node_tree.links.new(GammaNode_Detail.inputs["Color"], ImageTextureNodeList[bitm + 1].outputs["Color"])

                                    GammaNode_Detail.location.x = last_texture_x + TEXTURE_GAMMA_HORIZONTAL_PLACEMENT
                                    GammaNode_Detail.location.y = last_texture_y                     
                                    GammaNode_Detail.hide = True
                                elif(ShaderItem.bitmap_list[bitm].type == "detail_map3"):
                                    #create Gamma Node
                                    GammaNode_Detail = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
                                    GammaNode_Detail.inputs.get("Gamma").default_value = gamma_value

                                    #link Gamma Node
                                    pymat_copy.node_tree.links.new(GammaNode_Detail.inputs["Color"], ImageTextureNodeList[bitm + 1].outputs["Color"])

                                    GammaNode_Detail.location.x = last_texture_x + TEXTURE_GAMMA_HORIZONTAL_PLACEMENT
                                    GammaNode_Detail.location.y = last_texture_y                     
                                    GammaNode_Detail.hide = True                                    
                                elif(ShaderItem.bitmap_list[bitm].type == "bump_map"):
                                    #create Gamma Node
                                    GammaNode_Bump = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
                                    GammaNode_Bump.inputs.get("Gamma").default_value = gamma_value

                                    #link Gamma Node
                                    pymat_copy.node_tree.links.new(GammaNode_Bump.inputs["Color"], ImageTextureNodeList[bitm + 1].outputs["Color"])

                                    GammaNode_Bump.location.x = last_texture_x + TEXTURE_GAMMA_HORIZONTAL_PLACEMENT
                                    GammaNode_Bump.location.y = last_texture_y                     
                                    GammaNode_Bump.hide = True
                                elif(ShaderItem.bitmap_list[bitm].type == "bump_detail_map"):
                                    #create Gamma Node
                                    GammaNode_BumpDetail = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
                                    GammaNode_BumpDetail.inputs.get("Gamma").default_value = gamma_value

                                    #link Gamma Node
                                    pymat_copy.node_tree.links.new(GammaNode_BumpDetail.inputs["Color"], ImageTextureNodeList[bitm + 1].outputs["Color"])

                                    GammaNode_BumpDetail.location.x = last_texture_x + TEXTURE_GAMMA_HORIZONTAL_PLACEMENT
                                    GammaNode_BumpDetail.location.y = last_texture_y 
                                    GammaNode_BumpDetail.hide = True
                                elif(ShaderItem.bitmap_list[bitm].type == "self_illum_map"):
                                    #create Gamma Node
                                    GammaNode_SelfIllum = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
                                    GammaNode_SelfIllum.inputs.get("Gamma").default_value = gamma_value

                                    #link Gamma Node
                                    pymat_copy.node_tree.links.new(GammaNode_SelfIllum.inputs["Color"], ImageTextureNodeList[bitm + 1].outputs["Color"])

                                    GammaNode_SelfIllum.location.x = last_texture_x + TEXTURE_GAMMA_HORIZONTAL_PLACEMENT
                                    GammaNode_SelfIllum.location.y = last_texture_y 
                                    GammaNode_SelfIllum.hide = True
                                elif(ShaderItem.bitmap_list[bitm].type == "self_illum_detail_map"):
                                    #create Gamma Node
                                    GammaNode_SelfIllumDetail = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
                                    GammaNode_SelfIllumDetail.inputs.get("Gamma").default_value = gamma_value

                                    #link Gamma Node
                                    pymat_copy.node_tree.links.new(GammaNode_SelfIllumDetail.inputs["Color"], ImageTextureNodeList[bitm + 1].outputs["Color"])

                                    GammaNode_SelfIllumDetail.location.x = last_texture_x + TEXTURE_GAMMA_HORIZONTAL_PLACEMENT
                                    GammaNode_SelfIllumDetail.location.y = last_texture_y                         
                                    GammaNode_SelfIllumDetail.hide = True
                                #terrain shaders    
                                elif(ShaderItem.bitmap_list[bitm].type == "base_map_m_0"):
                                    #create Gamma Node
                                    GammaNode_Base_M0 = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
                                    GammaNode_Base_M0.inputs.get("Gamma").default_value = gamma_value

                                    #link Gamma Node
                                    pymat_copy.node_tree.links.new(GammaNode_Base_M0.inputs["Color"], ImageTextureNodeList[bitm + 1].outputs["Color"])

                                    GammaNode_Base_M0.location.x = last_texture_x + TEXTURE_GAMMA_HORIZONTAL_PLACEMENT
                                    GammaNode_Base_M0.location.y = last_texture_y                     
                                    GammaNode_Base_M0.hide = True
                                elif(ShaderItem.bitmap_list[bitm].type == "base_map_m_1"):
                                    #create Gamma Node
                                    GammaNode_Base_M1 = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
                                    GammaNode_Base_M1.inputs.get("Gamma").default_value = gamma_value

                                    #link Gamma Node
                                    pymat_copy.node_tree.links.new(GammaNode_Base_M1.inputs["Color"], ImageTextureNodeList[bitm + 1].outputs["Color"])

                                    GammaNode_Base_M1.location.x = last_texture_x + TEXTURE_GAMMA_HORIZONTAL_PLACEMENT
                                    GammaNode_Base_M1.location.y = last_texture_y                         
                                    GammaNode_Base_M1.hide = True
                                elif(ShaderItem.bitmap_list[bitm].type == "base_map_m_2"):
                                    #create Gamma Node
                                    GammaNode_Base_M2 = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
                                    GammaNode_Base_M2.inputs.get("Gamma").default_value = gamma_value

                                    #link Gamma Node
                                    pymat_copy.node_tree.links.new(GammaNode_Base_M2.inputs["Color"], ImageTextureNodeList[bitm + 1].outputs["Color"])

                                    GammaNode_Base_M2.location.x = last_texture_x + TEXTURE_GAMMA_HORIZONTAL_PLACEMENT
                                    GammaNode_Base_M2.location.y = last_texture_y 
                                    GammaNode_Base_M2.hide = True
                                elif(ShaderItem.bitmap_list[bitm].type == "base_map_m_3"):
                                    #create Gamma Node
                                    GammaNode_Base_M3 = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
                                    GammaNode_Base_M3.inputs.get("Gamma").default_value = gamma_value

                                    #link Gamma Node
                                    pymat_copy.node_tree.links.new(GammaNode_Base_M3.inputs["Color"], ImageTextureNodeList[bitm + 1].outputs["Color"])   
             
                                    GammaNode_Base_M3.location.x = last_texture_x + TEXTURE_GAMMA_HORIZONTAL_PLACEMENT
                                    GammaNode_Base_M3.location.y = last_texture_y  
                                    GammaNode_Base_M3.hide = True
                                elif(ShaderItem.bitmap_list[bitm].type == "detail_map_m_0"):
                                    #create Gamma Node
                                    GammaNode_Detail_M0 = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
                                    GammaNode_Detail_M0.inputs.get("Gamma").default_value = gamma_value

                                    #link Gamma Node
                                    pymat_copy.node_tree.links.new(GammaNode_Detail_M0.inputs["Color"], ImageTextureNodeList[bitm + 1].outputs["Color"])                     

                                    GammaNode_Detail_M0.location.x = last_texture_x + TEXTURE_GAMMA_HORIZONTAL_PLACEMENT
                                    GammaNode_Detail_M0.location.y = last_texture_y 
                                    GammaNode_Detail_M0.hide = True
                                elif(ShaderItem.bitmap_list[bitm].type == "detail_map_m_1"):
                                    #create Gamma Node
                                    GammaNode_Detail_M1 = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
                                    GammaNode_Detail_M1.inputs.get("Gamma").default_value = gamma_value

                                    #link Gamma Node
                                    pymat_copy.node_tree.links.new(GammaNode_Detail_M1.inputs["Color"], ImageTextureNodeList[bitm + 1].outputs["Color"])  

                                    GammaNode_Detail_M1.location.x = last_texture_x + TEXTURE_GAMMA_HORIZONTAL_PLACEMENT
                                    GammaNode_Detail_M1.location.y = last_texture_y                         
                                    GammaNode_Detail_M1.hide = True
                                elif(ShaderItem.bitmap_list[bitm].type == "detail_map_m_2"):
                                    #create Gamma Node
                                    GammaNode_Detail_M2 = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
                                    GammaNode_Detail_M2.inputs.get("Gamma").default_value = gamma_value

                                    #link Gamma Node
                                    pymat_copy.node_tree.links.new(GammaNode_Detail_M2.inputs["Color"], ImageTextureNodeList[bitm + 1].outputs["Color"])  

                                    GammaNode_Detail_M2.location.x = last_texture_x + TEXTURE_GAMMA_HORIZONTAL_PLACEMENT
                                    GammaNode_Detail_M2.location.y = last_texture_y 
                                    GammaNode_Detail_M2.hide = True
                                elif(ShaderItem.bitmap_list[bitm].type == "detail_map_m_3"):
                                    #create Gamma Node
                                    GammaNode_Detail_M3 = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
                                    GammaNode_Detail_M3.inputs.get("Gamma").default_value = gamma_value

                                    #link Gamma Node
                                    pymat_copy.node_tree.links.new(GammaNode_Detail_M3.inputs["Color"], ImageTextureNodeList[bitm + 1].outputs["Color"])                          

                                    GammaNode_Detail_M3.location.x = last_texture_x + TEXTURE_GAMMA_HORIZONTAL_PLACEMENT
                                    GammaNode_Detail_M3.location.y = last_texture_y                     
                                    GammaNode_Detail_M3.hide = True
                                elif(ShaderItem.bitmap_list[bitm].type == "bump_map_m_0"):
                                    #create Gamma Node
                                    GammaNode_Bump_M0 = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
                                    GammaNode_Bump_M0.inputs.get("Gamma").default_value = gamma_value

                                    #link Gamma Node
                                    pymat_copy.node_tree.links.new(GammaNode_Bump_M0.inputs["Color"], ImageTextureNodeList[bitm + 1].outputs["Color"])                      
             
                                    GammaNode_Bump_M0.location.x = last_texture_x + TEXTURE_GAMMA_HORIZONTAL_PLACEMENT
                                    GammaNode_Bump_M0.location.y = last_texture_y  
                                    GammaNode_Bump_M0.hide = True
                                elif(ShaderItem.bitmap_list[bitm].type == "bump_map_m_1"):
                                    #create Gamma Node
                                    GammaNode_Bump_M1 = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
                                    GammaNode_Bump_M1.inputs.get("Gamma").default_value = gamma_value

                                    #link Gamma Node
                                    pymat_copy.node_tree.links.new(GammaNode_Bump_M1.inputs["Color"], ImageTextureNodeList[bitm + 1].outputs["Color"])  

                                    GammaNode_Bump_M1.location.x = last_texture_x + TEXTURE_GAMMA_HORIZONTAL_PLACEMENT
                                    GammaNode_Bump_M1.location.y = last_texture_y 
                                    GammaNode_Bump_M1.hide = True
                                elif(ShaderItem.bitmap_list[bitm].type == "bump_map_m_2"):
                                    #create Gamma Node
                                    GammaNode_Bump_M2 = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
                                    GammaNode_Bump_M2.inputs.get("Gamma").default_value = gamma_value

                                    #link Gamma Node
                                    pymat_copy.node_tree.links.new(GammaNode_Bump_M2.inputs["Color"], ImageTextureNodeList[bitm + 1].outputs["Color"])  

                                    GammaNode_Bump_M2.location.x = last_texture_x + TEXTURE_GAMMA_HORIZONTAL_PLACEMENT
                                    GammaNode_Bump_M2.location.y = last_texture_y 
                                    GammaNode_Bump_M2.hide = True
                                elif(ShaderItem.bitmap_list[bitm].type == "bump_map_m_3"):
                                    #create Gamma Node
                                    GammaNode_Bump_M3 = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
                                    GammaNode_Bump_M3.inputs.get("Gamma").default_value = gamma_value

                                    #link Gamma Node
                                    pymat_copy.node_tree.links.new(GammaNode_Bump_M3.inputs["Color"], ImageTextureNodeList[bitm + 1].outputs["Color"])

                                    GammaNode_Bump_M3.location.x = last_texture_x + TEXTURE_GAMMA_HORIZONTAL_PLACEMENT
                                    GammaNode_Bump_M3.location.y = last_texture_y 
                                    GammaNode_Bump_M3.hide = True
                                elif(ShaderItem.bitmap_list[bitm].type == "detail_bump_m_0"):
                                    #create Gamma Node
                                    GammaNode_Detail_Bump_M0 = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
                                    GammaNode_Detail_Bump_M0.inputs.get("Gamma").default_value = gamma_value

                                    #link Gamma Node
                                    pymat_copy.node_tree.links.new(GammaNode_Detail_Bump_M0.inputs["Color"], ImageTextureNodeList[bitm + 1].outputs["Color"])  

                                    GammaNode_Detail_Bump_M0.location.x = last_texture_x + TEXTURE_GAMMA_HORIZONTAL_PLACEMENT
                                    GammaNode_Detail_Bump_M0.location.y = last_texture_y 
                                    GammaNode_Detail_Bump_M0.hide = True
                                elif(ShaderItem.bitmap_list[bitm].type == "detail_bump_m_1"):
                                    #create Gamma Node
                                    GammaNode_Detail_Bump_M1 = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
                                    GammaNode_Detail_Bump_M1.inputs.get("Gamma").default_value = gamma_value

                                    #link Gamma Node
                                    pymat_copy.node_tree.links.new(GammaNode_Detail_Bump_M1.inputs["Color"], ImageTextureNodeList[bitm + 1].outputs["Color"]) 

                                    GammaNode_Detail_Bump_M1.location.x = last_texture_x + TEXTURE_GAMMA_HORIZONTAL_PLACEMENT
                                    GammaNode_Detail_Bump_M1.location.y = last_texture_y 
                                    GammaNode_Detail_Bump_M1.hide = True
                                elif(ShaderItem.bitmap_list[bitm].type == "detail_bump_m_2"):
                                    #create Gamma Node
                                    GammaNode_Detail_Bump_M2 = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
                                    GammaNode_Detail_Bump_M2.inputs.get("Gamma").default_value = gamma_value

                                    #link Gamma Node
                                    pymat_copy.node_tree.links.new(GammaNode_Detail_Bump_M2.inputs["Color"], ImageTextureNodeList[bitm + 1].outputs["Color"]) 

                                    GammaNode_Detail_Bump_M2.location.x = last_texture_x + TEXTURE_GAMMA_HORIZONTAL_PLACEMENT
                                    GammaNode_Detail_Bump_M2.location.y = last_texture_y 
                                    GammaNode_Detail_Bump_M2.hide = True
                                elif(ShaderItem.bitmap_list[bitm].type == "detail_bump_m_3"):
                                    #create Gamma Node
                                    GammaNode_Detail_Bump_M3 = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
                                    GammaNode_Detail_Bump_M3.inputs.get("Gamma").default_value = gamma_value

                                    #link Gamma Node
                                    pymat_copy.node_tree.links.new(GammaNode_Detail_Bump_M3.inputs["Color"], ImageTextureNodeList[bitm + 1].outputs["Color"])                        

                                    GammaNode_Detail_Bump_M3.location.x = last_texture_x + TEXTURE_GAMMA_HORIZONTAL_PLACEMENT
                                    GammaNode_Detail_Bump_M3.location.y = last_texture_y 
                                    GammaNode_Detail_Bump_M3.hide = True
                                else:
                                    print("Unhandled texture type trying to be assinged a Gamma Node")


                                #make_gamma(pymat_copy.node_tree, ImageTextureNodeList[bitm + 1], ShaderItem.bitmap_list[bitm].type, 2.00)                    
                                # #create Gamma Node
                                # GammaNode = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
                                # GammaNode.inputs.get("Gamma").default_value = 2.00
                                
                                # #link Image Texture to Gamma
                                # pymat_copy.node_tree.links.new(GammaNode.inputs["Color"], ImageTextureNodeList[bitm + 1].outputs["Color"])

                            elif(ShaderItem.bitmap_list[bitm].curve_option == 3 and bitmap_error != 1): #curve = linear
                                ImageTextureNodeList[bitm + 1].image.colorspace_settings.name = "Linear"
                            elif(ShaderItem.bitmap_list[bitm].curve_option == 4 and bitmap_error != 1): #curve = offset log
                                ImageTextureNodeList[bitm + 1].image.colorspace_settings.name = "Linear"
                            elif(ShaderItem.bitmap_list[bitm].curve_option == 5 and bitmap_error != 1): #curve = sRGB
                                ImageTextureNodeList[bitm + 1].image.colorspace_settings.name = "sRGB"
                            elif(ShaderItem.bitmap_list[bitm].curve_option == 6 and bitmap_error != 1): #curve = Default Data
                                ImageTextureNodeList[bitm + 1].image.colorspace_settings.name = "Linear"
                            else:
                                print("Curve Data Error!")
                            
                            
                            #location of texture and gamma nodes
                            if(texture_node_made == 1):
                                if(gamma_node_made == 1):
                                    ImageTextureNodeList[bitm + 1].location.x = last_texture_x 
                                    ImageTextureNodeList[bitm + 1].location.y = last_texture_y - TEXTURE_NODE_W_GAMMA_HORIZONTAL_SPACING
                                    
                                    last_node_x = last_texture_x 
                                    last_node_y = last_texture_y - TEXTURE_NODE_W_GAMMA_HORIZONTAL_SPACING

                                    
                                    ImageTextureNodeList[bitm + 1].hide = True               
                                else:   
                                    ImageTextureNodeList[bitm + 1].location.x = last_texture_x
                                    ImageTextureNodeList[bitm + 1].location.y = last_texture_y                        
                                    
                                    last_node_x = last_texture_x
                                    last_node_y = last_texture_y          
                                  
                                    ImageTextureNodeList[bitm + 1].hide = True
                            
                            
                            
                            
                            
                            #all shader files
                            #Sets all textures to Channel Packed
                            if(bitmap_error != 1):
                                ImageTextureNodeList[bitm + 1].image.alpha_mode = "CHANNEL_PACKED"
                            


                            #print("scale uniform entering if: " + str(ShaderItem.bitmap_list[bitm].scale_uniform))
                            #print("scale xy entering if: " + str(ShaderItem.bitmap_list[bitm].scale_xy))
                            #print("trans xy entering if: " + str(ShaderItem.bitmap_list[bitm].translation_xy))
                            
                            #CREATE SCALING NODES IF SCALING VALUES EXIST
                            if(ShaderItem.bitmap_list[bitm].scale_uniform != 1.00 or ShaderItem.bitmap_list[bitm].scale_xy != [1.00,1.00] or ShaderItem.bitmap_list[bitm].translation_xy != [0.00,0.00]): #if the scale values are not default
                                #create scaling node
                                TexCoordNode = pymat_copy.node_tree.nodes.new('ShaderNodeTexCoord')
                                
                                #create mapping node
                                MappingNode = pymat_copy.node_tree.nodes.new('ShaderNodeMapping')
                                
                                #link together the TexCoord node and the Mapping node
                                pymat_copy.node_tree.links.new(MappingNode.inputs["Vector"],TexCoordNode.outputs["UV"]) #connects UV to Vector
                                
                                trans_node_made = 1
                                
                                print("TRANSFORM DATA FOUND. MAKING MAPPING NODES")
                                #Change the values for scale uniform and XY
                                if(ShaderItem.bitmap_list[bitm].scale_uniform != 1.00):
                                    MappingNode.inputs.get("Scale").default_value = [ShaderItem.bitmap_list[bitm].scale_uniform, ShaderItem.bitmap_list[bitm].scale_uniform, 1.00]
                                    
                                    #link to texture node
                                    #pymat_copy.node_tree.links.new(ImageTextureNodeList[bitm + 1].inputs["Vector"], MappingNode.outputs["Vector"])
                                    
                                if(ShaderItem.bitmap_list[bitm].scale_xy != [1.00,1.00]):
                                    MappingNode.inputs.get("Scale").default_value = [ShaderItem.bitmap_list[bitm].scale_xy[0], ShaderItem.bitmap_list[bitm].scale_xy[1], 1.00]
                                    
                                    #link to texture node
                                    #pymat_copy.node_tree.links.new(ImageTextureNodeList[bitm + 1].inputs["Vector"], MappingNode.outputs["Vector"])
                                if(ShaderItem.bitmap_list[bitm].translation_xy != [0.00,0.00]):
                                    MappingNode.inputs.get("Location").default_value = [ShaderItem.bitmap_list[bitm].translation_xy[0], ShaderItem.bitmap_list[bitm].translation_xy[1], 0.00]
                                    
                                    #link to texture node
                                    #pymat_copy.node_tree.links.new(ImageTextureNodeList[bitm + 1].inputs["Vector"], MappingNode.outputs["Vector"])
                            
                                print("Wrap Option: " + str(ShaderItem.bitmap_list[bitm].wrap_option))
                                if (ShaderItem.bitmap_list[bitm].wrap_option == 3 or ShaderItem.bitmap_list[bitm].wrap_option == 13 or ShaderItem.bitmap_list[bitm].wrap_option == 2):
                                    print("making mirror map for " + ShaderItem.bitmap_list[bitm].type)
                                    
                                    #link texture to mirror group node
                                    MirrorGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Utility: XY Mirror Wrap")
                                    pymat_copy.node_tree.links.new(ImageTextureNodeList[bitm + 1].inputs["Vector"], MirrorGroup.outputs["Vector"])
                                    
                                    #link mapping to mirror group node
                                    pymat_copy.node_tree.links.new(MirrorGroup.inputs["Vector"], MappingNode.outputs["Vector"])
                                
                                    #works for current iteration of the Mirror Nodes being at 47 meters in both X and Y
                                    #Check for extra shift due to texture resolution ratio
                                    if(ShaderItem.bitmap_list[bitm].width / ShaderItem.bitmap_list[bitm].height == (2/2)): #if the ratio is 1:1 then shift down Y by 3 meters
                                        MirrorGroup = shift_mirror_wrap(MirrorGroup)
                                    
                                    mirror_node_made = 1
                                elif (ShaderItem.bitmap_list[bitm].wrap_option == 4 or ShaderItem.bitmap_list[bitm].wrap_option == 5):
                                    print("making mirror map for " + ShaderItem.bitmap_list[bitm].type)
                                    
                                    #link texture to mirror group node
                                    MirrorGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Utility: X Mirror Wrap")
                                    pymat_copy.node_tree.links.new(ImageTextureNodeList[bitm + 1].inputs["Vector"], MirrorGroup.outputs["Vector"])
                                    
                                    #link mapping to mirror group node
                                    pymat_copy.node_tree.links.new(MirrorGroup.inputs["Vector"], MappingNode.outputs["Vector"])                    
                                
                                    #Check for extra shift due to texture resolution ratio
                                    if(ShaderItem.bitmap_list[bitm].width / ShaderItem.bitmap_list[bitm].height == (2/2)): #if the ratio is 1:1 then shift down Y by 3 meters
                                        MirrorGroup = shift_mirror_wrap(MirrorGroup)
                                        
                                    mirror_node_made = 1
                                elif (ShaderItem.bitmap_list[bitm].wrap_option == 9 or ShaderItem.bitmap_list[bitm].wrap_option == 8):
                                    print("making mirror map for " + ShaderItem.bitmap_list[bitm].type)
                                    
                                    #link texture to mirror group node
                                    MirrorGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Utility: Y Mirror Wrap")
                                    pymat_copy.node_tree.links.new(ImageTextureNodeList[bitm + 1].inputs["Vector"], MirrorGroup.outputs["Vector"])
                                    
                                    #link mapping to mirror group node
                                    pymat_copy.node_tree.links.new(MirrorGroup.inputs["Vector"], MappingNode.outputs["Vector"]) 
                                    
                                    #Check for extra shift due to texture resolution ratio
                                    if(ShaderItem.bitmap_list[bitm].width / ShaderItem.bitmap_list[bitm].height == (2/2)): #if the ratio is 1:1 then shift down Y by 3 meters
                                        MirrorGroup = shift_mirror_wrap(MirrorGroup)
                                        
                                    mirror_node_made = 1
                                else:    
                                    #link to texture node
                                    pymat_copy.node_tree.links.new(ImageTextureNodeList[bitm + 1].inputs["Vector"], MappingNode.outputs["Vector"])
                            
                            #if no scale or translation data found BUT it is mirrored
                            else:
                                print("No scaling values found. Might make Mirror Node anyways")
                                print("Wrap Option: " + str(ShaderItem.bitmap_list[bitm].wrap_option))
                                if(ShaderItem.bitmap_list[bitm].wrap_option == 3 or ShaderItem.bitmap_list[bitm].wrap_option == 13 or ShaderItem.bitmap_list[bitm].wrap_option == 2):
                                    print("making mirror map for " + ShaderItem.bitmap_list[bitm].type)
                                    #create scaling node
                                    TexCoordNode = pymat_copy.node_tree.nodes.new('ShaderNodeTexCoord')
                                    
                                    #create mapping node
                                    MappingNode = pymat_copy.node_tree.nodes.new('ShaderNodeMapping')
                                    
                                    #link together the TexCoord node and the Mapping node
                                    pymat_copy.node_tree.links.new(MappingNode.inputs["Vector"],TexCoordNode.outputs["UV"]) #connects UV to Vector
                                    
                                    #link texture to mirror group node
                                    MirrorGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Utility: XY Mirror Wrap")
                                    pymat_copy.node_tree.links.new(ImageTextureNodeList[bitm + 1].inputs["Vector"], MirrorGroup.outputs["Vector"])
                              
                                    #link mapping to mirror group node
                                    pymat_copy.node_tree.links.new(MirrorGroup.inputs["Vector"], MappingNode.outputs["Vector"])       
                              
                                    #Check for extra shift due to texture resolution ratio
                                    if(ShaderItem.bitmap_list[bitm].width / ShaderItem.bitmap_list[bitm].height == (2/2)): #if the ratio is 1:1 then shift down Y by 3 meters
                                        MirrorGroup = shift_mirror_wrap(MirrorGroup)
                                        
                                    mirror_node_made = 1
                                    trans_node_made = 1
                                elif(ShaderItem.bitmap_list[bitm].wrap_option == 4 or ShaderItem.bitmap_list[bitm].wrap_option == 5):
                                    print("making mirror map for " + ShaderItem.bitmap_list[bitm].type)
                                    #create scaling node
                                    TexCoordNode = pymat_copy.node_tree.nodes.new('ShaderNodeTexCoord')
                                    
                                    #create mapping node
                                    MappingNode = pymat_copy.node_tree.nodes.new('ShaderNodeMapping')
                                    
                                    #link together the TexCoord node and the Mapping node
                                    pymat_copy.node_tree.links.new(MappingNode.inputs["Vector"],TexCoordNode.outputs["UV"]) #connects UV to Vector
                                    
                                    #link texture to mirror group node
                                    MirrorGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Utility: X Mirror Wrap")
                                    pymat_copy.node_tree.links.new(ImageTextureNodeList[bitm + 1].inputs["Vector"], MirrorGroup.outputs["Vector"])
                              
                                    #link mapping to mirror group node
                                    pymat_copy.node_tree.links.new(MirrorGroup.inputs["Vector"], MappingNode.outputs["Vector"])                      
                                
                                    #Check for extra shift due to texture resolution ratio
                                    if(ShaderItem.bitmap_list[bitm].width / ShaderItem.bitmap_list[bitm].height == (2/2)): #if the ratio is 1:1 then shift down Y by 3 meters
                                        MirrorGroup = shift_mirror_wrap(MirrorGroup)
                                        
                                    mirror_node_made = 1
                                    trans_node_made = 1
                                elif (ShaderItem.bitmap_list[bitm].wrap_option == 9 or ShaderItem.bitmap_list[bitm].wrap_option == 8):
                                    print("making mirror map for " + ShaderItem.bitmap_list[bitm].type)
                                    
                                    #if 
                                    #create scaling node
                                    TexCoordNode = pymat_copy.node_tree.nodes.new('ShaderNodeTexCoord')
                                    
                                    #create mapping node
                                    MappingNode = pymat_copy.node_tree.nodes.new('ShaderNodeMapping')
                                    
                                    #link together the TexCoord node and the Mapping node
                                    pymat_copy.node_tree.links.new(MappingNode.inputs["Vector"],TexCoordNode.outputs["UV"]) #connects UV to Vector
                                    
                                    #link texture to mirror group node
                                    MirrorGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Utility: Y Mirror Wrap")
                                    pymat_copy.node_tree.links.new(ImageTextureNodeList[bitm + 1].inputs["Vector"], MirrorGroup.outputs["Vector"])
                              
                                    #link mapping to mirror group node
                                    pymat_copy.node_tree.links.new(MirrorGroup.inputs["Vector"], MappingNode.outputs["Vector"])        
                 
                                    #Check for extra shift due to texture resolution ratio
                                    if(ShaderItem.bitmap_list[bitm].width / ShaderItem.bitmap_list[bitm].height == (2/2)): #if the ratio is 1:1 then shift down Y by 3 meters
                                        MirrorGroup = shift_mirror_wrap(MirrorGroup)
                                        
                                    mirror_node_made = 1
                                    trans_node_made = 1
                            
                            
                            #locations of scaling and mirror nodes
                            if(mirror_node_made == 1):
                                MirrorGroup.location.x = last_node_x - TEXTURE_MIRROR_NODE_HORIZONTAL_SPACING
                                MirrorGroup.location.y = last_node_y
                                
                                last_node_x = MirrorGroup.location.x
                                last_node_y = MirrorGroup.location.y
                            if(trans_node_made == 1):
                                MappingNode.location.x = last_node_x - TEXTURE_MAPPING_HORIZONTAL_SPACING
                                MappingNode.location.y = last_node_y
                                
                                last_node_x = MappingNode.location.x
                                last_node_y = MappingNode.location.y
                            
                                TexCoordNode.location.x = last_node_x - TEXTURE_COORD_NODE_HORIZONTAL_SPACING
                                TexCoordNode.location.y = last_node_y
                                
                                last_node_x = TexCoordNode.location.x
                                last_node_y = TexCoordNode.location.y                
                            
                                MappingNode.hide = True
                                TexCoordNode.hide = True
                            #POSSIBLY NOT NEEDED AT ALL
                            #LABEL TEXTURE GROUPS
                            if(ShaderItem.bitmap_list[bitm].type == "base_map"):
                                BaseMap = ImageTextureNodeList[bitm + 1].image
                            elif(ShaderItem.bitmap_list[bitm].type == "detail_map"):
                                DetailMap = ImageTextureNodeList[bitm + 1].image
                            elif(ShaderItem.bitmap_list[bitm].type == "bump_map"):
                                BumpMap = ImageTextureNodeList[bitm + 1].image            
                            elif(ShaderItem.bitmap_list[bitm].type == "bump_detail_map"):
                                BumpDetailMap = ImageTextureNodeList[bitm + 1].image            
                            elif(ShaderItem.bitmap_list[bitm].type == "self_illum_map"):
                                SelfIllumMap = ImageTextureNodeList[bitm + 1].image            
                            elif(ShaderItem.bitmap_list[bitm].type == "environment_map"):
                                EnvironmentMap = ImageTextureNodeList[bitm + 1].image    
                            else:
                                print("Texture is of a different type")            


                                                #ADD MORE POSSIBILITIES
                                                ###########################
                                                #CONNECT TEXTURES TO GROUPS
                                                ###########################

                            # .shader files
                                               
                            #BASE_MAP
                            #print("before base")
                            if((Shader_Type == 0 or Shader_Type == 2) and ShaderItem.bitmap_list[bitm].type == "base_map"): # and ShaderGroupList[bitm + 1] == "albedo"):
                                #if albedo option = constant_color
                                print("  trying to link base_map")
                                if (ShaderItem.albedo_option == 2):
                                    #- rgb node
                                    #if curve uses Gamma
                                    #print("  base 0a")
                                    if(ShaderItem.bitmap_list[bitm].curve_option == 1 or ShaderItem.bitmap_list[bitm].curve_option == 2):
                                        #link gamma to albedo
                                        pymat_copy.node_tree.links.new(AlbedoGroup.inputs[0], GammaNode_Base.outputs[0])
                                        #print("  base 0a1")
                                    else:
                                        #print("  base 0a2")
                                        #link base_map to albedo
                                        pymat_copy.node_tree.links.new(AlbedoGroup.inputs[0], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                #if albedo option is not constant color
                                
                                elif (ShaderItem.albedo_option != 2):
                                    #- rgb node
                                    #if curve uses Gamma
                                    #print("  base 1a")
                                    if(ShaderItem.bitmap_list[bitm].curve_option == 1 or ShaderItem.bitmap_list[bitm].curve_option == 2):
                                        print(str(ShaderItem.bitmap_list[bitm].curve_option))
                                        #print("  base 1a1")
                                        #link gamma to albedo
                                        pymat_copy.node_tree.links.new(AlbedoGroup.inputs[0], GammaNode_Base.outputs[0])
                                        pymat_copy.node_tree.links.new(AlbedoGroup.inputs[1], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                    else:
                                        #print("  base 1a2")
                                        #link base_map to albedo
                                        pymat_copy.node_tree.links.new(AlbedoGroup.inputs[0], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        pymat_copy.node_tree.links.new(AlbedoGroup.inputs[1], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                    #- a/spec node
                                    #if spec data comes from diffuse
                                    
                                    # if(ShaderItem.specular_mask_option == 1):
                                        # #print("  base 1a3")
                                        # pymat_copy.node_tree.links.new(AlbedoGroup.inputs[1], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                            #print("before detail map")
                            #DETAIL_MAP
                            if((Shader_Type == 0 or Shader_Type == 2) and ShaderItem.bitmap_list[bitm].type == "detail_map"): # and ShaderGroupList[bitm + 1] == "albedo"):
                                print("  trying to link detail_map")
                                #if albedo option is not constant color
                                if (ShaderItem.albedo_option != 2 and ShaderItem.material_model_option != 0):
                                    #print("  detail 0a")
                                    #- rgb node
                                    #if curve uses Gamma
                                    if(ShaderItem.bitmap_list[bitm].curve_option == 1 or ShaderItem.bitmap_list[bitm].curve_option == 2):
                                        #link gamma to albedo
                                        #print("  detail 0b")
                                        pymat_copy.node_tree.links.new(AlbedoGroup.inputs["detail_map.rgb"], GammaNode_Detail.outputs[0])
                                        pymat_copy.node_tree.links.new(AlbedoGroup.inputs["detail_map.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                    else:
                                        #link base_map to albedo
                                        #print("  detail 0c")
                                        pymat_copy.node_tree.links.new(AlbedoGroup.inputs["detail_map.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        pymat_copy.node_tree.links.new(AlbedoGroup.inputs["detail_map.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                    #- a/spec node
                                    #if spec data comes from diffuse
                                    # if(ShaderItem.specular_mask_option == 1):
                                        # #print("  detail 0d")
                                        # pymat_copy.node_tree.links.new(AlbedoGroup.inputs["detail_map.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])

                            #DETAIL_MAP2
                            if((Shader_Type == 0 or Shader_Type == 2) and ShaderItem.bitmap_list[bitm].type == "detail_map2"): # and ShaderGroupList[bitm + 1] == "albedo"):
                                print("  trying to link detail_map2")
                                #if albedo option is not constant color
                                if ((ShaderItem.albedo_option == 1 or ShaderItem.albedo_option == 5 or ShaderItem.albedo_option == 6 or ShaderItem.albedo_option == 7) and ShaderItem.material_model_option != 0):
                                    #print("  detail 0a")
                                    #- rgb node
                                    #if curve uses Gamma
                                    if(ShaderItem.bitmap_list[bitm].curve_option == 1 or ShaderItem.bitmap_list[bitm].curve_option == 2):
                                        #link gamma to albedo
                                        #print("  detail 0b")
                                        pymat_copy.node_tree.links.new(AlbedoGroup.inputs["detail_map2.rgb"], GammaNode_Detail.outputs[0])
                                        pymat_copy.node_tree.links.new(AlbedoGroup.inputs["detail_map2.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                    else:
                                        #link base_map to albedo
                                        #print("  detail 0c")
                                        pymat_copy.node_tree.links.new(AlbedoGroup.inputs["detail_map2.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        pymat_copy.node_tree.links.new(AlbedoGroup.inputs["detail_map2.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                    #- a/spec node
                                    #if spec data comes from diffuse
                                    # if(ShaderItem.specular_mask_option == 1):
                                        # #print("  detail 0d")
                                        # pymat_copy.node_tree.links.new(AlbedoGroup.inputs["detail_map.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])

                            #DETAIL_MAP3
                            if((Shader_Type == 0 or Shader_Type == 2) and ShaderItem.bitmap_list[bitm].type == "detail_map3"): # and ShaderGroupList[bitm + 1] == "albedo"):
                                print("  trying to link detail_map3")
                                #if albedo option is not constant color
                                if (ShaderItem.albedo_option == 5 and ShaderItem.material_model_option != 0):
                                    #print("  detail 0a")
                                    #- rgb node
                                    #if curve uses Gamma
                                    if(ShaderItem.bitmap_list[bitm].curve_option == 1 or ShaderItem.bitmap_list[bitm].curve_option == 2):
                                        #link gamma to albedo
                                        #print("  detail 0b")
                                        pymat_copy.node_tree.links.new(AlbedoGroup.inputs["detail_map3.rgb"], GammaNode_Detail.outputs[0])
                                        pymat_copy.node_tree.links.new(AlbedoGroup.inputs["detail_map3.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                    else:
                                        #link base_map to albedo
                                        #print("  detail 0c")
                                        pymat_copy.node_tree.links.new(AlbedoGroup.inputs["detail_map3.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        pymat_copy.node_tree.links.new(AlbedoGroup.inputs["detail_map3.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                    #- a/spec node
                                    #if spec data comes from diffuse
                                    # if(ShaderItem.specular_mask_option == 1):
                                        # #print("  detail 0d")
                                        # pymat_copy.node_tree.links.new(AlbedoGroup.inputs["detail_map.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                            
                            #BUMP MAP
                            #print("before bump")
                            if((Shader_Type == 0 or Shader_Type == 2) and ShaderItem.bitmap_list[bitm].type == "bump_map"): # and ShaderGroupList[bitm + 1] == "bump"):
                                print("  trying to link bump_map")
                                if (ShaderItem.bump_mapping_option != 0): #if bump_map option is not off    
                                    #print("  bump 0a")
                                    #if gamma exists
                                    #if(ShaderItem.bitmap_list[bitm].curve_option == 0, ShaderItem.bitmap_list[bitm].curve_option == 1, ShaderItem.bitmap_list[bitm].curve_option == 2):
                                    #    pymat_copy.node_tree.links.new(BumpGroup.inputs["bump_map"], GammaNode.outputs[0])
                                    #else: 
                                    pymat_copy.node_tree.links.new(BumpGroup.inputs["bump_map"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                            #DETAIL BUMP MAP
                            #print("before detail bump")
                            if((Shader_Type == 0 or Shader_Type == 2) and ShaderItem.bitmap_list[bitm].type == "bump_detail_map"): # and ShaderGroupList[bitm + 1] == "bump"):
                                print("  trying to link bump_detail_map")
                                if (ShaderItem.bump_mapping_option != 0 and ShaderItem.bump_mapping_option != 1): #if bump option is not off and not standard
                                    #print("  detail bump 0a")
                                    #if gamma exists
                                    #if(ShaderItem.bitmap_list[bitm].curve_option == 0, ShaderItem.bitmap_list[bitm].curve_option == 1, ShaderItem.bitmap_list[bitm].curve_option == 2):
                                    #    pymat_copy.node_tree.links.new(BumpGroup.inputs["bump_detail_map"], GammaNode.outputs[0])
                                    #else:
                                    pymat_copy.node_tree.links.new(BumpGroup.inputs["bump_detail_map"], ImageTextureNodeList[bitm + 1].outputs["Color"])

                            #SELF ILLUM MAP
                            if((Shader_Type == 0 or Shader_Type == 2) and ShaderItem.bitmap_list[bitm].type == "self_illum_map" and ShaderItem.self_illumination_option != 0):
                                print("  trying to link self_illum_map")
                                #if self illumination option == 1 2 5 7 8 9 10 11
                                if (ShaderItem.self_illumination_option == 1 or ShaderItem.self_illumination_option == 2 or ShaderItem.self_illumination_option == 5 or ShaderItem.self_illumination_option == 7 or ShaderItem.self_illumination_option == 8 or ShaderItem.self_illumination_option == 9 or ShaderItem.self_illumination_option == 10 or ShaderItem.self_illumination_option == 11):
                                    #if bitmap curve data uses Gamma then connect that
                                    if(ShaderItem.bitmap_list[bitm].curve_option == 1 or ShaderItem.bitmap_list[bitm].curve_option == 2):
                                        pymat_copy.node_tree.links.new(SelfIllumGroup.inputs["self_illum_map.rgb"], GammaNode_SelfIllum.outputs[0])
                                    else:
                                        pymat_copy.node_tree.links.new(SelfIllumGroup.inputs["self_illum_map.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                            
                            #SELF ILLUM DETAIL MAP
                            
                            
                            
                            
                            #ENVIRONMENT MAP 
                            
                            
                            #ALPHA_TEST_MAP
                            if((Shader_Type == 0 or Shader_Type == 2) and ShaderItem.alpha_test_option != 0 and ShaderItem.bitmap_list[bitm].type == "alpha_test_map" and (ShaderItem.alpha_test_option == 1 or ShaderItem.specular_mask_option == 2)):
                                pymat_copy.node_tree.links.new(AlphaTestGroup.inputs["alpha_test_map.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                            
                            #SPECULAR_MASK_TEXTURE
                            if(Shader_Type == 0 and ShaderItem.bitmap_list[bitm].type == "specular_mask_texture" and ShaderItem.specular_mask_option == 2 and ShaderItem.albedo_option != 2):
                                pymat_copy.node_tree.links.new(AlbedoGroup.inputs["base_map.a/specular_mask"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])                
                            
                            #Alpha_blend
                            if(Shader_Type == 0 and ShaderItem.bitmap_list[bitm].type == "base_map" and ShaderItem.blend_mode_option == 3):
                                pymat_copy.node_tree.links.new(AlphaBlendGroup.inputs["base_map.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])                 
                            elif(Shader_Type == 0 and ShaderItem.bitmap_list[bitm].type == "specular_mask_texture" and ShaderItem.blend_mode_option == 5):
                                pymat_copy.node_tree.links.new(AlphaBlendGroup.inputs["base_map.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])                 
                            
                            
                            #######################
                            # .shader_terrain files
                            #######################
                            
                            
                            if(Shader_Type == 1):
                                #MATERIAL 0 LINK
                                if(ShaderItem.bitmap_list[bitm].type == "base_map_m_0" and ShaderItem.material_0_option != 2):
                                    #print("  trying to link base_map_m_0")
                                    #- rgb node
                                    #if curve uses Gamma
                                    if(ShaderItem.bitmap_list[bitm].curve_option == 1 or ShaderItem.bitmap_list[bitm].curve_option == 2):
                                        #link gamma to albedo
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["base_map_m_0.rgb"], GammaNode_Base_M0.outputs[0])
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["base_map_m_0.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                    else:
                                        #link base_map_m_0 to terrain group m0
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["base_map_m_0.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["base_map_m_0.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                elif(ShaderItem.bitmap_list[bitm].type == "detail_map_m_0" and ShaderItem.material_0_option != 2):
                                    #print("  trying to link detail_map_m_0")
                                    #- rgb node
                                    #if curve uses Gamma
                                    if(ShaderItem.bitmap_list[bitm].curve_option == 1 or ShaderItem.bitmap_list[bitm].curve_option == 2):
                                        #link gamma to albedo
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["detail_map_m_0.rgb"], GammaNode_Detail_M0.outputs[0])
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["detail_map_m_0.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                    else:
                                        #link detail_map_m_0 to terrain group m0
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["detail_map_m_0.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["detail_map_m_0.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                elif(ShaderItem.bitmap_list[bitm].type == "bump_map_m_0" and ShaderItem.material_0_option != 2):
                                    #print("  trying to link bump_map_m_0")
                                    #- rgb node
                                    #if curve uses Gamma
                                    if(ShaderItem.bitmap_list[bitm].curve_option == 1 or ShaderItem.bitmap_list[bitm].curve_option == 2):
                                        #link gamma to albedo
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["bump_map_m_0"], GammaNode_Bump_M0.outputs[0])
                                    else:
                                        #link bump_map_m_0 to terrain group m0
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["bump_map_m_0"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                elif(ShaderItem.bitmap_list[bitm].type == "detail_bump_m_0" and ShaderItem.material_0_option != 2):
                                    #print("  trying to link detail_bump_m_0")
                                    #- rgb node
                                    #if curve uses Gamma
                                    if(ShaderItem.bitmap_list[bitm].curve_option == 1 or ShaderItem.bitmap_list[bitm].curve_option == 2):
                                        #link gamma to albedo
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["detail_bump_m_0"], GammaNode_Detail_Bump_M0.outputs[0])
                                    else:
                                        #link detail_bump_m_0 to terrain group m0
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["detail_bump_m_0"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                
                                #MATERIAL 1 LINK
                                if(ShaderItem.bitmap_list[bitm].type == "base_map_m_1" and ShaderItem.material_1_option != 2):
                                    #print("  trying to link base_map_m_1")
                                    #- rgb node
                                    #if curve uses Gamma
                                    if(ShaderItem.bitmap_list[bitm].curve_option == 1 or ShaderItem.bitmap_list[bitm].curve_option == 2):
                                        #link gamma to albedo
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["base_map_m_1.rgb"], GammaNode_Base_M1.outputs[0])
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["base_map_m_1.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                    else:
                                        #link base_map_m_1 to terrain group M1
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["base_map_m_1.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["base_map_m_1.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                elif(ShaderItem.bitmap_list[bitm].type == "detail_map_m_1" and ShaderItem.material_1_option != 2):
                                    #print("  trying to link detail_map_m_1")
                                    #- rgb node
                                    #if curve uses Gamma
                                    if(ShaderItem.bitmap_list[bitm].curve_option == 1 or ShaderItem.bitmap_list[bitm].curve_option == 2):
                                        #link gamma to albedo
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["detail_map_m_1.rgb"], GammaNode_Detail_M1.outputs[0])
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["detail_map_m_1.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                    else:
                                        #link detail_map_m_1 to terrain group M1
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["detail_map_m_1.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["detail_map_m_1.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                elif(ShaderItem.bitmap_list[bitm].type == "bump_map_m_1" and ShaderItem.material_1_option != 2):
                                    #print("  trying to link bump_map_m_1")
                                    #- rgb node
                                    #if curve uses Gamma
                                    if(ShaderItem.bitmap_list[bitm].curve_option == 1 or ShaderItem.bitmap_list[bitm].curve_option == 2):
                                        #link gamma to albedo
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["bump_map_m_1"], GammaNode_Bump_M1.outputs[0])
                                    else:
                                        #link bump_map_m_1 to terrain group M1
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["bump_map_m_1"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                elif(ShaderItem.bitmap_list[bitm].type == "detail_bump_m_1" and ShaderItem.material_1_option != 2):
                                    #print("  trying to link detail_bump_m_1")
                                    #- rgb node
                                    #if curve uses Gamma
                                    if(ShaderItem.bitmap_list[bitm].curve_option == 1 or ShaderItem.bitmap_list[bitm].curve_option == 2):
                                        #link gamma to albedo
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["detail_bump_m_1"], GammaNode_Detail_Bump_M1.outputs[0])
                                    else:
                                        #link detail_bump_m_1 to terrain group M1
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["detail_bump_m_1"], ImageTextureNodeList[bitm + 1].outputs["Color"])                

                                #MATERIAL 2 LINK
                                if(ShaderItem.bitmap_list[bitm].type == "base_map_m_2" and ShaderItem.material_2_option != 2):
                                    #print("  trying to link base_map_m_2")
                                    #- rgb node
                                    #if curve uses Gamma
                                    if(ShaderItem.bitmap_list[bitm].curve_option == 1 or ShaderItem.bitmap_list[bitm].curve_option == 2):
                                        #link gamma to albedo
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["base_map_m_2.rgb"], GammaNode_Base_M2.outputs[0])
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["base_map_m_2.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                    else:
                                        #link base_map_m_2 to terrain group M2
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["base_map_m_2.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["base_map_m_2.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                elif(ShaderItem.bitmap_list[bitm].type == "detail_map_m_2" and ShaderItem.material_2_option != 2):
                                    #print("  trying to link detail_map_m_2")
                                    #- rgb node
                                    #if curve uses Gamma
                                    if(ShaderItem.bitmap_list[bitm].curve_option == 1 or ShaderItem.bitmap_list[bitm].curve_option == 2):
                                        #link gamma to albedo
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["detail_map_m_2.rgb"], GammaNode_Detail_M2.outputs[0])
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["detail_map_m_2.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                    else:
                                        #link detail_map_m_2 to terrain group M2
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["detail_map_m_2.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["detail_map_m_2.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                elif(ShaderItem.bitmap_list[bitm].type == "bump_map_m_2" and ShaderItem.material_2_option != 2):
                                    #print("  trying to link bump_map_m_2")
                                    #- rgb node
                                    #if curve uses Gamma
                                    if(ShaderItem.bitmap_list[bitm].curve_option == 1 or ShaderItem.bitmap_list[bitm].curve_option == 2):
                                        #link gamma to albedo
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["bump_map_m_2"], GammaNode_Bump_M2.outputs[0])
                                    else:
                                        #link bump_map_m_2 to terrain group M2
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["bump_map_m_2"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                elif(ShaderItem.bitmap_list[bitm].type == "detail_bump_m_2" and ShaderItem.material_2_option != 2):
                                    #print("  trying to link detail_bump_m_2")
                                    #- rgb node
                                    #if curve uses Gamma
                                    if(ShaderItem.bitmap_list[bitm].curve_option == 1 or ShaderItem.bitmap_list[bitm].curve_option == 2):
                                        #link gamma to albedo
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["detail_bump_m_2"], GammaNode_Detail_Bump_M2.outputs[0])
                                    else:
                                        #link detail_bump_m_2 to terrain group M2
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["detail_bump_m_2"], ImageTextureNodeList[bitm + 1].outputs["Color"]) 

                                #MATERIAL 3 LINK
                                if(ShaderItem.bitmap_list[bitm].type == "base_map_m_3" and ShaderItem.material_3_option != 0):
                                    #print("  trying to link base_map_m_3")
                                    #- rgb node
                                    #if curve uses Gamma
                                    if(ShaderItem.bitmap_list[bitm].curve_option == 1 or ShaderItem.bitmap_list[bitm].curve_option == 2):
                                        #link gamma to albedo
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["base_map_m_3.rgb"], GammaNode_Base_M3.outputs[0])
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["base_map_m_3.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                    else:
                                        #link base_map_m_3 to terrain group M3
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["base_map_m_3.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["base_map_m_3.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                elif(ShaderItem.bitmap_list[bitm].type == "detail_map_m_3" and ShaderItem.material_3_option != 0):
                                    #print("  trying to link detail_map_m_3")
                                    #- rgb node
                                    #if curve uses Gamma
                                    if(ShaderItem.bitmap_list[bitm].curve_option == 1 or ShaderItem.bitmap_list[bitm].curve_option == 2):
                                        #link gamma to albedo
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["detail_map_m_3.rgb"], GammaNode_Detail_M3.outputs[0])
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["detail_map_m_3.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                    else:
                                        #link detail_map_m_3 to terrain group M3
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["detail_map_m_3.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["detail_map_m_3.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                elif(ShaderItem.bitmap_list[bitm].type == "bump_map_m_3" and ShaderItem.material_3_option != 0):
                                    #print("  trying to link bump_map_m_3")
                                    #- rgb node
                                    #if curve uses Gamma
                                    if(ShaderItem.bitmap_list[bitm].curve_option == 1 or ShaderItem.bitmap_list[bitm].curve_option == 2):
                                        #link gamma to albedo
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["bump_map_m_3"], GammaNode_Bump_M3.outputs[0])
                                    else:
                                        #link bump_map_m_3 to terrain group M3
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["bump_map_m_3"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                elif(ShaderItem.bitmap_list[bitm].type == "detail_bump_m_3"):
                                    #print("  trying to link detail_bump_m_3" and ShaderItem.material_3_option != 0)
                                    #- rgb node
                                    #if curve uses Gamma
                                    if(ShaderItem.bitmap_list[bitm].curve_option == 1 or ShaderItem.bitmap_list[bitm].curve_option == 2):
                                        #link gamma to albedo
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["detail_bump_m_3"], GammaNode_Detail_Bump_M3.outputs[0])
                                    else:
                                        #link detail_bump_m_3 to terrain group M3
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["detail_bump_m_3"], ImageTextureNodeList[bitm + 1].outputs["Color"])

                            
                                                #########################
                                                #SEPARATE COLOR NODE LINK
                                                #########################      
                                                # NOW BLEND TEXTURE LINK
                            
                            if(ShaderItem.bitmap_list[bitm].type == "blend_map"):
                                pymat_copy.node_tree.links.new(TerrainGroup.inputs["blend_map.rgb"],ImageTextureNodeList[bitm + 1].outputs["Color"])
                                pymat_copy.node_tree.links.new(TerrainGroup.inputs["blend_map.a"],ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                
                                #pymat_copy.node_tree.links.new(SeparateColorGroup.inputs["Color"],ImageTextureNodeList[bitm + 1].outputs["Color"])
                                
                               # if(ShaderItem.material_3_option != 0): #if material 3 is not off
                                    #pymat_copy.node_tree.links.new(TerrainGroupM3.inputs["blend_map_channel"],ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                            # #LINK TEXTURES TO GROUPS
                            # if (ShaderItem.albedo_option == 2): #albedo option = constant color
                                # pymat_copy.node_tree.links.new(AlbedoGroup.inputs["albedo.rgb"], GammaNode.outputs["Color"])
                                    
                        
                        #reset MIRROR_PADDING
                        MIRROR_PADDING = 0
                        
                        #add extra padding if mirror node was made
                        if(mirror_node_made == 1):
                            MIRROR_PADDING = TEXTURE_GAMMA_HORIZONTAL_PLACEMENT
                            
                            
                        if ImageTextureNodeList[bitm + 1] is None:
                            #delete the NoneType blank image texture
                            pymat_copy.node_tree.nodes.remove(ImageTextureNodeList[bitm + 1])
                            
                            last_texture_x = before_no_tex_x
                            last_texture_y = before_no_tex_y
                    else:
                        print(ShaderItem.bitmap_list[bitm].type + " is disabled") 
                        
                        #delete the NoneType blank image texture
                        pymat_copy.node_tree.nodes.remove(ImageTextureNodeList[bitm + 1])
                        
                        last_texture_x = before_no_tex_x
                        last_texture_y = before_no_tex_y
                        

                ShaderList.append(ShaderItem)
                ShaderList_Index = ShaderList_Index + 1
        wm.progress_end()
    # #Enable and activate Node Arrange
    # bpy.ops.preferences.addon_enable(module = "node_arrange")
    # #bpy.ops.node.button()
    # for area in bpy.context.screen.areas:
        # if area.type == 'NODE_EDITOR':
            # for region in area.regions:
                # if region.type == 'WINDOW':
                    # ctx = bpy.context.copy()
                    # ctx['area'] = area
                    # ctx['region'] = region
                    # bpy.ops.node.button(ctx, "INVOKE_DEFAULT")
        
    # bpy.ops.node.button()

    print("   _.---.                       .---.")
    print("  '---,  `.___________________.'  _  `.")
    print("       )   ___________________   <_>  :")
    print("  .---'  .'   / <'     '> \   `.     .'")
    print("   `----'    (  / @   @ \  )    `---'")
    print("              \(_ _\_/_ _)/")
    print("            (\ `-/     \-' /)")
    print('             "===\     /==="')
    print("              .==')___(`==.  ")  
    print("             ' .='     `=.")
    print("Thank you for using Halo 3 CR4B Tool!")
    print("Support: https://discord.gg/haloarchive")



#classes for the add-on





#Add-On Properties
class CR4BAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__
    export_path: bpy.props.StringProperty(
        name="Halo Asset Export Path",
        subtype='FILE_PATH'
    )
    node_group_file: bpy.props.StringProperty(
        name="Shader .blend File",
        subtype='FILE_PATH'
    )
    halo3_tag_path: bpy.props.StringProperty(
        name="Halo 3 Tags",
        subtype='FILE_PATH'
    )
    odst_tag_path: bpy.props.StringProperty(
        name="Halo 3: ODST Tags",
        subtype='FILE_PATH'
    )
    reach_tag_path: bpy.props.StringProperty(
        name="Halo Reach Tags",
        subtype='FILE_PATH'
    )

    def draw(self, context):
        layout = self.layout
        layout.row().label(text="Directory of ripped Halo Assets:")
        layout.row().prop(self, "export_path")
        layout.row().label(text="Directory Shader .blend file:")
        layout.row().prop(self, "node_group_file")
        layout.row().label(text="Directory Locations of Tag Files:")
        layout.row().prop(self, "halo3_tag_path")
        layout.row().prop(self, "odst_tag_path")
        layout.row().prop(self, "reach_tag_path")

class ProgressBarPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_progress_bar"
    bl_label = "Progress Bar"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    
    def draw(self, context):
        layout = self.layout
        
        # Create a progress bar in the center of the panel
        progress = context.window_manager.progress
        
        row = layout.row()
        row.label(text="Setting Up Materials:")
        row.prop(progress, "value", text="")


#Panel Properties
class CR4BAddonPanel(bpy.types.Panel):
    bl_label = "CR4B Tool"
    bl_idname = "OBJECT_PT_CR4B_Tool"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'CR4B Tool'

    def draw(self, context):
        layout = self.layout
        #spot_light_props = context.scene.spot_light_props
        
        #Area on Panel for Appending node groups
        layout.row().label(text="Append Shader Groups")
        layout.operator("test_addon.append_node_group", text="Append Node Group")
        
        # layout.row().label(text="")
        
        # # #Area on Panel for Creating Lights
        # layout.row().label(text="Light Properties")
        # layout.prop(spot_light_props, "light_type", text="Type")
        # layout.prop(spot_light_props, "light_size", text="Light Size")
        # layout.prop(spot_light_props, "light_strength", text="Light Strength")
        # layout.prop(spot_light_props, "light_color", text="Light Color")

        # layout.operator("object.add_spot_light", text="Create Light")
        
        layout.row().label(text="")
        
        #Area on Panel for Starting CR4B Tool
        layout.row().label(text="Select Tags to use")
        layout.row().prop(context.scene, "tag_dropdown")
        layout.row().label(text="Texture Image Format")
        layout.row().prop(context.scene, "image_format")
        layout.row().label(text="Start CR4B Tool")
        layout.row().operator("script.start_cr4b_tool")


#class for spotlight button properties on panel
# class SpotLightProperties(bpy.types.PropertyGroup):
    # light_types = [
        # ("POINT", "Point", "", 1),
        # ("SUN", "Sun", "", 2),
        # ("SPOT", "Spot", "", 3),
        # ("AREA", "Area", "", 4)
    # ]
    # light_type: bpy.props.EnumProperty(
        # items=light_types,
        # name="Light Type",
        # default="SPOT",
        # description="Choose the type of light to create"
    # )
    # light_size: bpy.props.FloatProperty(
        # name="Size",
        # description="Size of the Spot Light",
        # default=1.0,
        # min=0.1,
        # max=10.0
    # )
    # light_color: bpy.props.FloatVectorProperty(
        # name="Color",
        # description="Color of the Spot Light",
        # default=(1.0, 1.0, 1.0),
        # min=0.0,
        # max=1.0,
        # subtype='COLOR'
    # )
    # light_strength: bpy.props.FloatProperty(
        # name="Strength",
        # description="Strength of the Spot Light",
        # default=1.0,
        # min=0.1,
        # max=10.0
    # )

# #Button functionality for Add Light Button
# class AddSpotLightOperator(bpy.types.Operator):
    # bl_idname = "object.add_spot_light"
    # bl_label = "Add Spot Light"
    # bl_options = {'REGISTER', 'UNDO'}

    # def execute(self, context):
        # scene = context.scene
        # spot_light_props = scene.spot_light_props
        
        # light_type = spot_light_props.light_type
        # light_size = spot_light_props.light_size
        # light_color = spot_light_props.light_color
        # light_strength = spot_light_props.light_strength
        
        # if light_type == 'POINT':
            # bpy.ops.object.light_add(type='POINT', radius=light_size)
        # elif light_type == 'SUN':
            # bpy.ops.object.light_add(type='SUN', radius=light_size)
        # elif light_type == 'SPOT':
            # bpy.ops.object.light_add(type='SPOT', radius=light_size)
        # elif light_type == 'AREA':
            # bpy.ops.object.light_add(type='AREA', size=light_size)
        
        # light = bpy.context.object
        # light.data.color = light_color
        # light.data.energy = light_strength
        
        # #If viewport is viewed through a Camera
        # if context.space_data.region_3d.view_perspective == 'CAMERA':
            # print("passed view perspective if statement")
            # bpy.ops.view3d.snap_cursor_to_center()
            # #bpy.ops.object.editmode_toggle()
            # #bpy.ops.mesh.select_all(action='DESELECT')
            # #bpy.ops.object.editmode_toggle()

            # # Get the 3D cursor position
            # # Get the 3D cursor position
            # # Get the current scene and the active camera
            # # Get the active camera and the scene
            # # Get the active camera and the scene
            # camera = bpy.context.scene.camera
            # scene = bpy.context.scene


            # # Get the active viewport
            # for area in bpy.context.screen.areas:
                # if area.type == 'VIEW_3D':
                    # region = area.regions[-1]
                    # break

            # # Get the center of the viewport
            # x, y = region.width // 2, region.height // 2

            # # Get the view direction from the active region_3d
            # region_3d = bpy.context.space_data.region_3d
            # ray_origin = region_3d.view_location
            # ray_direction = region_3d.view_rotation @ mathutils.Vector((0, 0, -1))

            # # Cast a ray from the center of the viewport
            # depsgraph = bpy.context.evaluated_depsgraph_get()
            # result = bpy.context.scene.ray_cast(depsgraph, ray_origin, ray_direction)

            # if result[0]:
                # hit_object = bpy.context.scene.objects[result[3]]
                # if hit_object is not None and hit_object.type == 'MESH':
                    # if len(hit_object.data.materials) > 1:
                        # material_index = result[4]
                        # hit_material = hit_object.data.materials[material_index]
                        # print("Hit material: ", hit_material.name)
                    # else:
                        # print("Hit object: ", hit_object.name)
                # else:
                    # print("Hit object is None or not a mesh")
            # else:
                # print("Raycast didn't hit any objects")



            # # Loop through all the objects in the scene
            # for obj in scene.objects:
                # # Check if the object is a MESH type object
                # if obj.type == 'MESH':
                    # # Calculate the direction vector from the camera to the object
                    # direction = obj.location - camera.location

                    # # Cast a ray from the camera in the direction of the object
                    # result, location, normal, index = obj.ray_cast(camera.location, direction) #.normalized())

                    # # Check if the ray hit the object and that the hit point is in front of the camera
                    # if result and (location - camera.location).dot(camera.matrix_world.to_quaternion() @ Matrix(camera.data.view_frame())[-1].to_4d().to_3d()) > 0:
                        # print("The camera is looking at the " + obj.name + " object")
            
#test
            # obj = bpy.context.object
            # center = bpy.context.region_data.view_location
            # result, location, normal, index = obj.ray_cast(obj.matrix_world.inverted() @ center, obj.matrix_world.to_quaternion() @ -bpy.context.scene.camera.matrix_world.to_quaternion() @ Vector((0.0, 0.0, -1.0)))

            # if result:
                # print("result = True")
        
            #if bpy.context.object:
                #bpy.ops.object.select_all        
                #obj = bpy.context.object
                #if obj.type == 'MESH':
                    #print("Object is of type MESH")
                    # co, no, index = obj.ray_cast(bpy.context.scene.cursor.location, obj.matrix_world.to_quaternion() * Vector((0.0, 0.0, -1.0)))[:3]
                    # if index != -1:
                        # light.location = co
                        # light.rotation_euler = obj.matrix_world.to_quaternion() * no.to_track_quat('Z','Y').to_euler()
                # Get the active object and the viewport center
        
        
        
        
        # obj = bpy.context.object
        # center = bpy.context.region_data.view_location

        # # Cast a ray from the viewport center and check if it hits the object
        # result, location, normal, index = obj.ray_cast(obj.matrix_world.inverted() @ center, obj.matrix_world.to_quaternion() @ -bpy.context.scene.camera.matrix_world.to_quaternion() @ (0.0, 0.0, -1.0))

        # if result:
            # # Create a Spot Light
            # light_data = bpy.data.lights.new(name="SpotLight", type='SPOT')
            # light = bpy.data.objects.new(name="SpotLight", object_data=light_data)
            # bpy.context.scene.collection.objects.link(light)

            # # Place the light at the hit location and align it with the surface normal
            # light.location = location
            # light.rotation_mode = 'QUATERNION'
            # light.rotation_quaternion = normal.to_track_quat('Z', 'Y')                

        #return {'FINISHED'}
        
        # obj_at_cursor = bpy.context.scene.objects.active
        # if obj_at_cursor:
            # cursor_location = bpy.context.scene.cursor.location
            # obj_at_cursor.select_set(state=True)
            # bpy.context.view_layer.objects.active = obj_at_cursor
            # bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
            # bpy.context.scene.cursor.location = cursor_location
            # spot_light.parent = obj_at_cursor
            # spot_light.location = (0.0, 0.0, 0.0)
        # else:
            # spot_light.location = bpy.context.scene.cursor.location

        # scene.collection.objects.link(spot_light)
        # bpy.context.view_layer.objects.active = spot_light
        # return {'FINISHED'}


#class for appending node groups using button
class TestAddonAppendNodeGroup(bpy.types.Operator):
    bl_idname = "test_addon.append_node_group"
    bl_label = "Append Node Group"

    def execute(self, context):
        filepath = context.preferences.addons[__name__].preferences.node_group_file
        node_group_name = "[APPEND] Halo 3 Categories" # replace with the name of your node group

        if node_group_name in bpy.data.node_groups:
            return {'CANCELLED'}

        with bpy.data.libraries.load(filepath) as (data_from, data_to):
            data_to.node_groups = [node_group_name]

        # for node_group in data_to.node_groups:
            # bpy.context.scene.node_tree.nodes.new("ShaderNodeGroup")
            # bpy.context.scene.node_tree.nodes.active.node_tree = node_group

        return {'FINISHED'}


def update_halo3_tag_path(self, context):
    print("inside halo3_tag_path update")
    # Do something when the value of halo3_tag_path is updated
    pass

def update_odst_tag_path(self, context):
    # Do something when the value of odst_tag_path is updated
    pass

def update_reach_tag_path(self, context):
    # Do something when the value of reach_tag_path is updated
    pass  
    
def update_export_path(self, context):
    # Do something when the value of reach_tag_path is updated
    pass     



# #function that updates the values once the button is clicked
# def run_cr4b_tool(context):
    # tag_type = context.scene.tag_dropdown
    # if tag_type == 'Halo 3':
        # print("Trying to update halo3 tag path")
        # update_halo3_tag_path(context.scene, context.scene.halo3_tag_path)
    # elif tag_type == 'Halo 3: ODST':
        # update_odst_tag_path(context.scene, context.scene.odst_tag_path)
    # elif tag_type == 'Halo Reach':
        # update_reach_tag_path(context.scene, context.scene.reach_tag_path)
    # else:
        # # Handle error, no tag type selected
        # pass

class StartCR4BTool(bpy.types.Operator):
    bl_label = "Start CR4B Tool"
    bl_idname = "script.start_cr4b_tool"

    def execute(self, context):
        #run_cr4b_tool(context)
        Start_CR4B_Tool()
        return {'FINISHED'}

def update_dropdown(self, context):
    print("Selected Tags:", self.tag_dropdown)
    
    
def update_halo3_tag_path(self, context):
    print("Halo 3 Tags Path:", self.halo3_tag_path)    
    context.scene.halo3_tag_path = self.halo3_tag_path

def update_odst_tag_path(self, context):
    print("Halo 3: ODST Tags Path:", self.odst_tag_path) 
    context.scene.odst_tag_path = self.odst_tag_path
    
def update_reach_tag_path(self, context):
    print("Halo Reach Tags Path:", self.reach_tag_path) 
    context.scene.reach_tag_path = self.reach_tag_path
  
def update_export_path(self, context):
    print("Export Path:", self.export_path) 
    context.scene.export_path = self.export_path  
    
def register():
                    #Add-on Properties
    bpy.utils.register_class(CR4BAddonPreferences)
    bpy.utils.register_class(TestAddonAppendNodeGroup)
    bpy.types.Scene.halo3_tag_path = bpy.props.StringProperty(name="Halo 3 Tags Directory", default="", update=update_halo3_tag_path)
    bpy.types.Scene.odst_tag_path = bpy.props.StringProperty(name="Halo 3: ODST Tags Directory", default="", update=update_odst_tag_path)
    bpy.types.Scene.reach_tag_path = bpy.props.StringProperty(name="Halo Reach Tags Directory", default="", update=update_reach_tag_path)
    bpy.types.Scene.export_path = bpy.props.StringProperty(name="Ripped Asset Export Directory", default="", update=update_export_path)
    
    
    
                    #Panel Properties
    #Light Tool Properties
    #bpy.utils.register_class(SpotLightProperties)
    #bpy.utils.register_class(AddSpotLightOperator)
    #bpy.types.Scene.spot_light_props = bpy.props.PointerProperty(type=SpotLightProperties)
    
    #CR4B Tool Properties
    bpy.types.Scene.image_format = bpy.props.StringProperty(name="Image Format", default='.png')
    bpy.types.Scene.tag_dropdown = bpy.props.EnumProperty(
        items=[
            ("Halo 3", "Halo 3", "Tags for Halo 3"),
            ("Halo 3: ODST", "Halo 3: ODST", "Tags for Halo 3: ODST"),
            ("Halo Reach", "Halo Reach", "Tags for Halo Reach")
        ],
        name="Tags",
        description="Choose Tags to use for this Blender scene",
        update=update_dropdown
    )
    bpy.utils.register_class(CR4BAddonPanel)
    bpy.utils.register_class(StartCR4BTool)

def unregister():
     
    
                    #Add-On Properties
    del bpy.types.Scene.halo3_tag_path
    del bpy.types.Scene.odst_tag_path
    del bpy.types.Scene.reach_tag_path
    del bpy.types.Scene.export_path


                    #Panel Properties
    #Light Tool Properties                
    #bpy.utils.unregister_class(SpotLightProperties)
    #bpy.utils.unregister_class(AddSpotLightOperator)  
    #del bpy.types.Scene.spot_light_props
                    
    #CR4B Tool Properties
    del bpy.types.Scene.image_format
    bpy.utils.unregister_class(CR4BAddonPreferences)
    bpy.utils.unregister_class(CR4BAddonPanel)
    bpy.utils.unregister_class(StartCR4BTool)
    bpy.utils.unregister_class(TestAddonAppendNodeGroup)

if __name__ == "__main__":
    register()





#TODO STILL

#FIX SUPPORT FOR PREFIXES TO TELL WHERE .SHADER FILES SHOULD COME FROM

#If default values are needed, spawn them and make sure they get plugged in!


#Add a toggle so that if the code were to break, it continues instead. better user experience

# SOLVE HUGE BUG where when there are multiple .shader files that match, it reads the data from the wrong one
#(pymat_copy.e for the fusion coil)!
#  tends to cause default textures to be used when they shouldn't be

#add .biped tag reading support to get the Primary and Secondary Change Color values
#decal support - make them not cast shadows
#make sure time period for functions is grabbing
#add more support for default values plugging in

#add function support for bitmaps (like base_maps, detail_maps, etc)
#make list of ALL bitmaps that have "unknown" curve option
#base_map gamma is attaching to two points
# -terrain_shader support
# -foliage_shader support
# -if .bitmapfile doesn't exist when reading curve data then replace directory with default option
# -more edgecases for other shader combinations
# -self_illum support
# -self_illum detail support
#mirror mapping like this: https://cdn.discordapp.com/attachments/830517591184506972/1061725239018520626/image.png
#function support
#animations support?





























    
        #TexImage.bl_idname = "TexImage" + str(bitm)
        #TexImage.image = 
 

# def image_has_alpha(img):
    # b = 32 if img.is_float else 8
    # return (
        # img.depth == 2b or   # Grayscale+Alpha
        # img.depth == 4b      # RGB+Alpha
    # )




 
    #i.specular_color = 
    #i.specular_intensity =
    
    
    # # accessing all the nodes in that material
    # nodes = material.node_tree.nodes
            
    # # you can find the specific node by it's name
    # noise_node = nodes.get("Noise Texture")

    # # available inputs of that node
    # # print([x.identifier for x in noise_node.inputs])
    # # ['Vector', 'W', 'Scale', 'Detail', 'Distortion']

    # # change value of "W"
    # noise_node.inputs.get("W").default_value = 1

# # Since you want a Principled BSDF and the Material Output node
# # in your material, we can re-use the nodes that are automatically
# # created.
# principled_bsdf = nodes.get("Principled BSDF")
# material_output = nodes.get("Material Output")

# # Create Image Texture node and load the base color texture
# base_color = nodes.new('ShaderNodeTexImage')
# base_color.image = bpy.data.images.load(base_color_path)

# # Create Image Texture node and load the normal map
# normal_tex = nodes.new('ShaderNodeTexImage')
# normal_tex.image = bpy.data.images.load(normal_map_path)

# # Set the color space to non-color, since normal maps contain
# # the direction of the surface normals and not color data
# normal_tex.image.colorspace_settings.name = "Non-Color"

# # Create the Displacement node
# displacement = nodes.new('ShaderNodeDisplacement')

# # Connect the base color texture to the Principled BSDF
# links.new(principled_bsdf.inputs["Base Color"], base_color.outputs["Color"])

# # Connect the normal map to the Displacement node
# links.new(displacement.inputs["Height"], normal_tex.outputs["Color"])

# # Connect the Displacement node to the Material Output node
# links.new(material_output.inputs["Displacement"], displacement.outputs["Displacement"])



#gray_50_percent
    #base_map
    #self_illum
    #
    #
    #
  
#default_detail used
    #
    #
    #
    #
    #
    #

#CREATE NODE GROUP FOR CHIEFS SHADER
# You can do something like this: create the node group instance and set the existing node group as node tree for this new instance.

# import bpy

# C = bpy.context

# def instantiate_group(nodes, data_block_name):
    # group = nodes.new(type='ShaderNodeGroup')
    # group.node_tree = bpy.data.node_groups[data_block_name]
    # return group

# instantiate_group(C.object.material_slots[0].material.node_tree.nodes, 'NodeGroup')

#BITMAP OPTIONS
#options for bitmap_cruve
    #unknown
    #xRGB (gamma about 2.0)      gamma is really about 1.95
    #gamme 2.0
    #linear
    #sRGB


#IMPORT IMAGE TEXTURE NODE
#Import python
# import bpy
# from bpy import context, data, ops


# mat = bpy.data.materials.new(name="New_Mat")
# mat.use_nodes = True
# bsdf = mat.node_tree.nodes["Principled BSDF"]
# texImage = mat.node_tree.nodes.new('ShaderNodeTexImage')
# texImage.image = bpy.data.images.load("C:\\Users\\myName\\Downloads\\Textures\\Downloaded\\flooring5.jpg")
# mat.node_tree.links.new(bsdf.inputs['Base Color'], texImage.outputs['Color'])

# ob = context.view_layer.objects.active

# # Assign it to object
# if ob.data.materials:
    # ob.data.materials[0] = mat
# else:
    # ob.data.materials.append(mat)




#SHADER OPTIONS
#options for albedo
    # default
    # detail_blend
    # constant_color
    # two_change_color
    # four_change_color
    # three_detail_blend
    # two_detail_overlay
    # two_detail
    # color_mask
    # two_detail_black_point
    # two_change_color_anim_overlay
    # chameleon
    # two_change_color_chameleon
    # chameleon_masked
    # color_mask_hard_light
    # two_change_color_tex_overlay
    # chameleon_albedo_masked
    # custom_cube
    # two_color
    # scrolling_cube_mask
    # scrolling_cube
    # scrolling_texture_uv
    # texture_from_misc
#optons for bump_mapping
    # off
    # standard
    # detail
    # detail_masked
    # detail_plus_detail_masked
    # detail_unorm
#options for alpha_test
    # none
    # simple
#options for specular_map
    # no_specular_mask
    # specular_mask_from_diffuse
    # specular_mask_from_texture
    # specular_mask_from_color_texture
#options for material_model
    # diffuse_only
    # cook_torrance
    # two_lobe_phong
    # foliage
    # none
    # glass
    # organism
    # single_lobe_phong
    # car_paint
    # cook_torrance_custom_cube
    # cook_torrance_pbr_maps
    # cook_torrance_rim_fresnel
    # cook_torrance_scrolling_cube
    # cook_torrance_from_albedo
#options for environment_map
    # none
    # per_pixel
    # dynamic
    # from_flat_texture
    # custom_map
    # from_flat_exture_as_cubemap
#options for self_illumination
    # off
    # simple
    # 3_channel_self_illum
    # plasma
    # from_diffuse
    # illum_detail
    # meter
    # self_illum_times_diffuse
    # simple_with_alpha_mask
    # simple_four_change_color
    # illum_detail_world_space_four_cc
    # illum_change_color
#options for blend_mode
    # opaque
    # additive
    # multiply
    # alpha_blend
    # double_multiply
    # pre_multiplied_alpha
#options for parallax
    # off
    # simple
    # interpolated
    # simple_detail
#options for misc
    # first_person_never
    # first_person_sometimes
    # first_person_always
    # first_person_never_w/rotating_bitmaps




#loop through every model in blender scene
    #loop through each material slot
        #find .shader file with matching name
        #build class object with all that data
            #list
                #bitmap type (base_map, bump_map, etc)
                #bitmap name
                #bitmap directory
            #color tint values
            #scaling values for textures
        #spawn image texture for each bitmap found
        #create h3 shader by chief 
        
        
        
        
        
        
        #function notes
        
# 92 bytes after main offset is thr name of the function
# 36 bytes after name might be type of function
    # b'\x00' is basic
    # b'\x01' is basic?
    # b'\x08'  is curve 
    # b'\x03' is periodic
    # b'\x09' is exponent
    # b'\x02' is transition

#basic function
    # Time Period is 44 bytes after main offset
    # if 12 bytes in after function name is "tsgt" then no range name
        # if no range name, mark of tsgt_function_offset to be 12 bytes from function name
            # Min value is 28 bytes after tsgt_function_offset
            # Max value is 32 bytes after tsgt_function_offset
            # range toggle is at 25 bytes from tsgt_function_offset
                #int of 24 is toggle off
                #int of 25 is toggle on
            # function type/option is at 24 bytes from tsgt_function_offset
    # if 12 bytes in from function name is not "tsgt" then range name exists
        # set tsgt_function_offset to be after the end of range name - save it all as a string then use split() to chop off at 'tsgt' and save the front values as the range name and then find length of that for true offset start
            # Min value is 28 bytes after tsgt_function_offset
            # Max value is 32 bytes after tsgt_function_offset
            # range toggle is at 25 bytes from tsgt_function_offset
                #int of 24 is toggle off
                #int of 25 is toggle on
            # function type/option is at 24 bytes from tsgt_function_offset 
            
#curve function
    # Time Period is 44 bytes after main offset
    # if 12 bytes in after function name is "tsgt" then no range name
        # if no range name, mark start of tsgt_function_offset to be 12 bytes from function name
            # Min value is 28 bytes after tsgt_function_offset
            # Max value is 32 bytes after tsgt_function_offset
            # range toggle is at 25 bytes from tsgt_function_offset
                #int of 24 is toggle off
                #int of 25 is toggle on
            # function type/option is at 24 bytes from tsgt_function_offset
    # if 12 bytes in from function name is not "tsgt" then range name exists
        # set tsgt_function_offset to be after the end of range name - save it all as a string then use split() to chop off at 'tsgt' and save the front values as the range name and then find length of that for true offset start
            # Min value is 28 bytes after tsgt_function_offset
            # Max value is 32 bytes after tsgt_function_offset
            # range toggle is at 25 bytes from tsgt_function_offset
                #int of 24 is toggle off
                #int of 25 is toggle on
            # function type/option is at 24 bytes from tsgt_function_offset 
 
 
#periodic options:
# 0 - one
# 1 - zero
# 2 - cosine
# 3 - cosine [variable period]
# 4 - diagonal wave
# 5 - diagonal wave [variable period]
# 6 - slide
# 7 - slide [variable period]    
# 8 - noise
# 9 - jitter
# 10 - wander
# 11 - spark          
       
#periodic function
    # Time Period is 44 bytes after main offset
    # if 12 bytes in after function name is "tsgt" then no range name
        # range toggle is at 25 bytes from tsgt_function_offset
            #int of 24 is toggle off
            #int of 25 is toggle on
        # function type/option is at 24 bytes from tsgt_function_offset
        # Min value of chart is 28 bytes after tsgt_function_offset
        # Max value of chart is 32 bytes after tsgt_function_offset
        
        # Left Side function is at 56 bytes after tsgt_function_offset is 1 byte int
        # Left Side frequency value is at 60 bytes after tsgt_function_offset
        # Left Side phase value is at 64 bytes after tsgt_function_offset
        # Left Side min value is at 68 bytues after tsgt_function_offset
        # Left Side max value is at 72 bytes after tsgt_function_offset
        # Right Side function is at 76 bytes after tsgt_function_offset is 1 byte int
        # Right Side frequency value is at 80 bytes after tsgt_function_offset
        # Right side phase value is at 84 bytes after tsgt_function_offset
        # Right side min value is at 88 bytes after tsgt_function_offset
        # Right side max value is at 92 bytes after tsgt_function_offset
        # All abvoe info seems to repeat for 2nd line at 80 bytes from tsgt_function_offset
    # if 12 bytes in from function name is not "tsgt" then range name exists
        # set tsgt_function_offset to be after the end of range name - save it all as a string then use split() to chop off at 'tsgt' and save the front values as the range name and then find length of that for true offset start
        # range toggle is at 25 bytes from tsgt_function_offset
            #int of 24 is toggle off
            #int of 25 is toggle on
        # function type/option is at 24 bytes from tsgt_function_offset
        # Min value of chart is 28 bytes after tsgt_function_offset
        # Max value of chart is 32 bytes after tsgt_function_offset
        # Left Side function is at 56 bytes after tsgt_function_offset is 1 byte int
        # Left Side frequency value is at 60 bytes after tsgt_function_offset
        # Left Side phase value is at 64 bytes after tsgt_function_offset
        # Left Side min value is at 68 bytues after tsgt_function_offset
        # Left Side max value is at 72 bytes after tsgt_function_offset
        # Right Side function is at 76 bytes after tsgt_function_offset is 1 byte int
        # Right Side frequency value is at 80 bytes after tsgt_function_offset
        # Right side phase value is at 84 bytes after tsgt_function_offset
        # Right side min value is at 88 bytes after tsgt_function_offset
        # Right side max value is at 92 bytes after tsgt_function_offset
        # All abvoe info seems to repeat for 2nd line at 80 bytes from tsgt_function_offset        
       
    
       
#exponent function
    # Time Period is 44 bytes after main offset
    # if 12 bytes in after function name is "tsgt" then no range name
        # function type/option is at 24 bytes from tsgt_function_offset        
        # range toggle is at 25 bytes from tsgt_function_offset
            #int of 24 is toggle off
            #int of 25 is toggle on
        # Min value of chart is 28 bytes after tsgt_function_offset
        # Max value of chart is 32 bytes after tsgt_function_offset
        
        # Left Side Min value is at 56 bytes from tsgt_function_offset
        # Left Side Max Value is at 60 bytes from tsgt_function_offset
        # Left Side Exponent Value is at 64 bytes from tsgt_function_offset
        # Right Side Min Value is at 68 bytes from tsgt_function_offset
        # Right Side Max value is at 72 bytes from tsgt_function_offset
        # Right Side Exponent value is at 76 bytes from tsgt_function_offset
        # All abvoe info seems to repeat for 2nd line at 80 bytes from tsgt_function_offset
    # if 12 bytes in from function name is not "tsgt" then range name exists
        # set tsgt_function_offset to be after the end of range name - save it all as a string then use split() to chop off at 'tsgt' and save the front values as the range name and then find length of that for true offset start
        # function type/option is at 24 bytes from tsgt_function_offset        
        # range toggle is at 25 bytes from tsgt_function_offset
            #int of 24 is toggle off
            #int of 25 is toggle on
        # Min value of chart is 28 bytes after tsgt_function_offset
        # Max value of chart is 32 bytes after tsgt_function_offset
        # Left Side Min value is at 56 bytes from tsgt_function_offset
        # Left Side Max Value is at 60 bytes from tsgt_function_offset
        # Left Side Exponent Value is at 64 bytes from tsgt_function_offset
        # Right Side Min Value is at 68 bytes from tsgt_function_offset
        # Right Side Max value is at 72 bytes from tsgt_function_offset
        # Right Side Exponent value is at 76 bytes from tsgt_function_offset
        # All abvoe info seems to repeat for 2nd line at 80 bytes from tsgt_function_offset
        
        
        
#transition options
# 0 - linear
# 1 - early
# 2 - very early
# 3 - late
# 4 - very late
# 5 - cosine
# 6 - one
# 7 - zero
        
#transition function
    # Time Period is 44 bytes after main offset
    # if 12 bytes in after function name is "tsgt" then no range name
        # function type/option is at 24 bytes from tsgt_function_offset
        # range toggle is at 25 bytes from tsgt_function_offset
            #int of 24 is toggle off
            #int of 25 is toggle on
        # Min value of chart is 28 bytes after tsgt_function_offset
        # Max value of chart is 32 bytes after tsgt_function_offset
        
        # Left Side function option at 56 bytes in from tsgt_function_offset and it is 1 byte int
        # Left Side Min value is at 60 bytes in from tsgt_function_offset
        # Left Side Max value is at 64 bytes in from tsgt_function_offset
        # Right Side function option is at 68 bytes in from tsgt_function_offset and it is 1 byte int
        # Right Side Min value is at 72 bytes in from tsgt_function_offset
        # Right Side max value is at 76 bytes in from tsgt_function_offset
        # All abvoe left/right info seems to repeat for 2nd line at 80 bytes from tsgt_function_offset
   
   # if 12 bytes in from function name is not "tsgt" then range name exists
        # set tsgt_function_offset to be after the end of range name - save it all as a string then use split() to chop off at 'tsgt' and save the front values as the range name and then find length of that for true offset start        
        # function type/option is at 24 bytes from tsgt_function_offset
        # range toggle is at 25 bytes from tsgt_function_offset
            #int of 24 is toggle off
            #int of 25 is toggle on
        # Min value of chart is 28 bytes after tsgt_function_offset
        # Max value of chart is 32 bytes after tsgt_function_offset
        # Left Side function option at 56 bytes in from tsgt_function_offset and it is 1 byte int
        # Left Side Min value is at 60 bytes in from tsgt_function_offset
        # Left Side Max value is at 64 bytes in from tsgt_function_offset
        # Right Side function option is at 68 bytes in from tsgt_function_offset and it is 1 byte int
        # Right Side Min value is at 72 bytes in from tsgt_function_offset
        # Right Side max value is at 76 bytes in from tsgt_function_offset
        # All abvoe left/right info seems to repeat for 2nd line at 80 bytes from tsgt_function_offset

