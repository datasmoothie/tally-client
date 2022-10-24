build_default_formats = {
    'base_label':{
        'bold': False,
        'align': "right"        
    },
    'base': {
        'bold': False,
        'align': "center"
    },
    'stats': {
        'bold': False,
        'align': "center"
    },
    "percentage": {
        'num_format': "0\%",
        'bold': False,
        'align': "center"
    },
    "counts": {
        'num_format': "0", # No commas
        'bold': False,
        'align': "center"
    },
    "sig_test": {
        'num_format': "#.#",
        'bold': False,
        'align': "center"
    },
    "sub_column":{
        "border": None, #continous border
        "top": 0,
        "bottom": 0,
        "text_wrap": True
    },
    "super_column":{
        "bold": True,
        "text_wrap": True
    },
    "sub_index":{
        "align": "right",
        "valign": "vcenter",
        "right": 0,
        "text_wrap": True
    },
    "super_index":{
        "bold": True,
        "align": "left",
        "valign": "vcenter",
        "text_wrap": True,
        "top": 0,
        "right": 0
    },

    "row_colors": [ "FFFFFF", "FFFFFF" ],

    "offsets": {
        "top": 6,
        "left": 0,
        "column": 1,  # This is how many cells we shift from the left
        "row": 2  # This is how many rows we shift from the top,
    },

    "set_page_setup": {"hide_gridlines":{"option":2}}

#    "set_rows":[
#        {"row":6,
#            "height":100,
#            "format":{"border":1, "bold":True}}
#    ],


}
