
# eventually the warnings here should be errors, causing casa --pipeline to exit

pipelineOK = True

try:
    import pipeline
except:
    print("WARN: could not import pipeline")
    pipelineOK = False

if  pipelineOK:
    try:
        pipeline.initcli()
    except:
        print("WARN: pipeline.initcli() failed")
