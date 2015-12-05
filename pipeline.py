import routez
#
import heuristic_melody_detection as hmd, valid_filenames as valfiles, calculatefeatures as calcfeats, compression as comp, construct_transformed_feature_action_map as construct_tfam, generate_random_policy as grp

scripts = []
#scripts += [hmd.Main, valfiles.Main] 
scripts += [calcfeats.Main, comp.Main, construct_tfam.Main, grp.Main]
for script in scripts:
    script()
#try:
#    for script in scripts:
#        script()
#except Exception as e:
#    import inspect
#    frm = inspect.trace()[-1]
#    mod = inspect.getmodule(frm[0])
#    modname = mod.__name__ if mod else frm[1]
#    print('Error during execution of script: '+ modname)
