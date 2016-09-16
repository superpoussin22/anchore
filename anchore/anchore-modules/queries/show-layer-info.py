#!/usr/bin/env python

import sys
import os
import re
import json
import traceback

import anchore.anchore_utils

# main routine

try:
    config = anchore.anchore_utils.init_query_cmdline(sys.argv, "params: all ...\nhelp: shows dockerfile lines, associated layer IDs, and layer sizes")
except Exception as err:
    print str(err)
    sys.exit(1)

if not config:
    sys.exit(0)

if len(config['params']) <= 0:
    print "Query requires input: all|onlyimage ..."


warns = list()
outlist = list()

showall = True
if config['params'][0] == 'onlyimage':
    outlist.append(["ImageID", "Repo/Tags", "LayerId", "LayerSize", "DockerfileLine"])
    showall = False
else:
    outlist.append(["ImageID", "Repo/Tags", "LayerId", "LayerSize", "DockerfileLine", "InheritedFromParent"])    

try:
    ftreetypes = {}
    idata = anchore.anchore_utils.load_image_report(config['imgid'])
    for fid in idata['familytree']:
        fdata = anchore.anchore_utils.load_image_report(fid)
        ftreetypes[fid] = fdata['meta']['usertype']

    ddata = anchore.anchore_utils.load_analysis_output(config['imgid'], 'layer_info', 'layers_to_dockerfile')
    ddata_list = json.loads(ddata['dockerfile_to_layer_map'])
    inherited = False
    for record in ddata_list:
        layer = record['layer']
        if not inherited:
            if layer != config['imgid']:
                if layer in ftreetypes:
                    if ftreetypes[layer] and ftreetypes[layer] != "none":
                        inherited = True
        if showall:
            outlist.append([config['meta']['shortId'], config['meta']['humanname'], record['layer'], record['layer_sizebytes'], '_'.join(record['dockerfile_line'].split()), str(inherited)])
        else:
            if not inherited:
                outlist.append([config['meta']['shortId'], config['meta']['humanname'], record['layer'], record['layer_sizebytes'], '_'.join(record['dockerfile_line'].split())])
                
    pass

except Exception as err:
    # handle the case where something wrong happened
    import traceback
    traceback.print_exc()
    warns.append("query error: "+str(err))
    pass

# handle the no match case
if len(outlist) < 1:
    #outlist.append(["NOMATCH", "NOMATCH", "NOMATCH"])
    pass

anchore.anchore_utils.write_kvfile_fromlist(config['output'], outlist)

if len(warns) > 0:
    anchore.anchore_utils.write_plainfile_fromlist(config['output_warns'], warns)

sys.exit(0)


