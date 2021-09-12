

for each_sample in ['BH_ER_050417', 'BH_ER_110816', 'CB_ER_080217']:
    for each_rep in [1, 2, 3]:
        spades_cmd = 'spades.py --meta --only-assembler -1 %s_%s_pairedForward.fastq -2 %s_%s_pairedReverse.fastq -o %s_%s_spades_wd -t 16' % (each_sample, each_rep, each_sample, each_rep, each_sample, each_rep)
        print(spades_cmd)

# spades.py --meta -1 Kelp_R1.fastq -2 Kelp_R2.fastq -o BH_ER_050417_SPAdes_wd -t 12 -k 21,33,55,75,99,127