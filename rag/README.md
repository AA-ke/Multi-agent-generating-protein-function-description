<h1>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/images/nf-core-pairgenomealign_logo_dark.png">
    <img alt="nf-core/pairgenomealign" src="docs/images/nf-core-pairgenomealign_logo_light.png">
  </picture>
</h1>

[![GitHub Actions CI Status](https://github.com/nf-core/pairgenomealign/actions/workflows/ci.yml/badge.svg)](https://github.com/nf-core/pairgenomealign/actions/workflows/ci.yml)
[![GitHub Actions Linting Status](https://github.com/nf-core/pairgenomealign/actions/workflows/linting.yml/badge.svg)](https://github.com/nf-core/pairgenomealign/actions/workflows/linting.yml)[![AWS CI](https://img.shields.io/badge/CI%20tests-full%20size-FF9900?labelColor=000000&logo=Amazon%20AWS)](https://nf-co.re/pairgenomealign/results)[![Cite with Zenodo](http://img.shields.io/badge/DOI-10.5281/zenodo.13910535-1073c8?labelColor=000000)](https://doi.org/10.5281/zenodo.13910535)
[![nf-test](https://img.shields.io/badge/unit_tests-nf--test-337ab7.svg)](https://www.nf-test.com)

[![Nextflow](https://img.shields.io/badge/nextflow%20DSL2-%E2%89%A524.10.1-23aa62.svg)](https://www.nextflow.io/)
[![run with conda](http://img.shields.io/badge/run%20with-conda-3EB049?labelColor=000000&logo=anaconda)](https://docs.conda.io/en/latest/)
[![run with docker](https://img.shields.io/badge/run%20with-docker-0db7ed?labelColor=000000&logo=docker)](https://www.docker.com/)
[![run with singularity](https://img.shields.io/badge/run%20with-singularity-1d355c.svg?labelColor=000000)](https://sylabs.io/docs/)
[![Launch on Seqera Platform](https://img.shields.io/badge/Launch%20%F0%9F%9A%80-Seqera%20Platform-%234256e7)](https://cloud.seqera.io/launch?pipeline=https://github.com/nf-core/pairgenomealign)

[![Get help on Slack](http://img.shields.io/badge/slack-nf--core%20%23pairgenomealign-4A154B?labelColor=000000&logo=slack)](https://nfcore.slack.com/channels/pairgenomealign)[![Follow on Twitter](http://img.shields.io/badge/twitter-%40nf__core-1DA1F2?labelColor=000000&logo=twitter)](https://twitter.com/nf_core)[![Follow on Mastodon](https://img.shields.io/badge/mastodon-nf__core-6364ff?labelColor=FFFFFF&logo=mastodon)](https://mstdn.science/@nf_core)[![Watch on YouTube](http://img.shields.io/badge/youtube-nf--core-FF0000?labelColor=000000&logo=youtube)](https://www.youtube.com/c/nf-core)

## Introduction

**nf-core/pairgenomealign** is a bioinformatics pipeline that aligns one or more _query_ genomes to a _target_ genome, and plots pairwise representations.

![Tubemap workflow summary](docs/images/pairgenomealign-tubemap.png "Tubemap workflow summary")

The main steps of the pipeline are:

1. Genome QC ([`assembly-scan`](https://github.com/rpetit3/assembly-scan)).
2. Genome indexing ([`lastdb`](https://gitlab.com/mcfrith/last/-/blob/main/doc/lastdb.rst)).
3. Genome pairwise alignments ([`lastal`](https://gitlab.com/mcfrith/last/-/blob/main/doc/lastal.rst)).
4. Alignment plotting ([`last-dotplot`](https://gitlab.com/mcfrith/last/-/blob/main/doc/last-dotplot.rst)).
5. Alignment export to various formats with [`maf-convert`](https://gitlab.com/mcfrith/last/-/blob/main/doc/maf-convert.rst), plus [`Samtools`](https://www.htslib.org/) for SAM/BAM/CRAM.

The pipeline can generate four kinds of outputs, called _many-to-many_, _many-to-one_, _one-to-many_ and _one-to-one_, depending on whether sequences of one genome are allowed match the other genome multiple times or not.

These alignments are output in [MAF](https://genome.ucsc.edu/FAQ/FAQformat.html#format5) format, and optional line plot representations are output in PNG format.

## Usage

> [!NOTE]
> If you are new to Nextflow and nf-core, please refer to [this page](https://nf-co.re/docs/usage/installation) on how to set-up Nextflow. Make sure to [test your setup](https://nf-co.re/docs/usage/introduction#how-to-run-a-pipeline) with `-profile test` before running the workflow on actual data.

First, prepare a samplesheet with your input data that looks as follows:

`samplesheet.csv`:

```csv
sample,fasta
query_1,path-to-query-genome-file-one.fasta
query_2,path-to-query-genome-file-two.fasta
```

Each row represents a fasta file, this can also contain multiple rows to accomodate multiple query genomes in fasta format.

Now, you can run the pipeline using:

```bash
nextflow run nf-core/pairgenomealign \
   -profile <docker/singularity/.../institute> \
   --target sequencefile.fa \
   --input samplesheet.csv \
   --outdir <OUTDIR>
```

> [!WARNING]
> Please provide pipeline parameters via the CLI or Nextflow `-params-file` option. Custom config files including those provided by the `-c` Nextflow option can be used to provide any configuration _**except for parameters**_; see [docs](https://nf-co.re/docs/usage/getting_started/configuration#custom-configuration-files).

For more details and further functionality, please refer to the [usage documentation](https://nf-co.re/pairgenomealign/usage) and the [parameter documentation](https://nf-co.re/pairgenomealign/parameters).

## Pipeline output

To see the results of an example test run with a full size dataset refer to the [results](https://nf-co.re/pairgenomealign/results) tab on the nf-core website pipeline page.
For more details about the output files and reports, please refer to the
[output documentation](https://nf-co.re/pairgenomealign/output).

## Credits

`nf-core/pairgenomealign` was originally written by [charles-plessy](https://github.com/charles-plessy); the original versions are available at <https://github.com/oist/plessy_pairwiseGenomeComparison>.

We thank the following people for their extensive assistance in the development of this pipeline:

- [Mahdi Mohammed](https://github.com/U13bs1125) ported the original pipeline to _nf-core_ template 2.14.x.
- [Martin Frith](https://github.com/mcfrith/), the author of LAST, gave us extensive feedback and advices.
- [Michael Mansfield](https://github.com/mjmansfi) tested the pipeline and provided critical comments.
- [Aleksandra Bliznina](https://github.com/aleksandrabliznina) contributed to the creation of the initial `last/*` modules.
- [Jiashun Miao](https://github.com/miaojiashun) and [Huyen Pham](https://github.com/ngochuyenpham) tested the pipeline on vertebrate genomes.

## Contributions and Support

If you would like to contribute to this pipeline, please see the [contributing guidelines](.github/CONTRIBUTING.md).

For further information or help, don't hesitate to get in touch on the [Slack `#pairgenomealign` channel](https://nfcore.slack.com/channels/pairgenomealign) (you can join with [this invite](https://nf-co.re/join/slack)).

## Citations

If you use this pipeline, please cite:

> **Extreme genome scrambling in marine planktonic Oikopleura dioica cryptic species.**
> Charles Plessy, Michael J. Mansfield, Aleksandra Bliznina, Aki Masunaga, Charlotte West, Yongkai Tan, Andrew W. Liu, Jan Grašič, María Sara del Río Pisula, Gaspar Sánchez-Serna, Marc Fabrega-Torrus, Alfonso Ferrández-Roldán, Vittoria Roncalli, Pavla Navratilova, Eric M. Thompson, Takeshi Onuma, Hiroki Nishida, Cristian Cañestro, Nicholas M. Luscombe.
> _Genome Res._ 2024. 34: 426-440; doi: [10.1101/2023.05.09.539028](https://doi.org/10.1101/gr.278295.123). PubMed ID: [38621828](https://pubmed.ncbi.nlm.nih.gov/38621828/)

[OIST research news article](https://www.oist.jp/news-center/news/2024/4/25/oikopleura-who-species-identity-crisis-genome-community)

And also please cite the [LAST papers](https://gitlab.com/mcfrith/last/-/blob/main/doc/last-papers.rst).

An extensive list of references for the tools used by the pipeline can be found in the [`CITATIONS.md`](CITATIONS.md) file.

You can cite the `nf-core` publication as follows:

> **The nf-core framework for community-curated bioinformatics pipelines.**
>
> Philip Ewels, Alexander Peltzer, Sven Fillinger, Harshil Patel, Johannes Alneberg, Andreas Wilm, Maxime Ulysse Garcia, Paolo Di Tommaso & Sven Nahnsen.
>
> _Nat Biotechnol._ 2020 Feb 13. doi: [10.1038/s41587-020-0439-x](https://dx.doi.org/10.1038/s41587-020-0439-x).


<h1>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/images/nf-core-methylseq_logo_dark.png">
    <img alt="nf-core/methylseq" src="docs/images/nf-core-methylseq_logo_light.png">
  </picture>
</h1>

[![GitHub Actions CI Status](https://github.com/nf-core/methylseq/actions/workflows/ci.yml/badge.svg)](https://github.com/nf-core/methylseq/actions/workflows/ci.yml)
[![GitHub Actions Linting Status](https://github.com/nf-core/methylseq/actions/workflows/linting.yml/badge.svg)](https://github.com/nf-core/methylseq/actions/workflows/linting.yml)[![AWS CI](https://img.shields.io/badge/CI%20tests-full%20size-FF9900?labelColor=000000&logo=Amazon%20AWS)](https://nf-co.re/methylseq/results)[![Cite with Zenodo](http://img.shields.io/badge/DOI-10.5281/zenodo.1343417-1073c8?labelColor=000000)](https://doi.org/10.5281/zenodo.1343417)
[![nf-test](https://img.shields.io/badge/unit_tests-nf--test-337ab7.svg)](https://www.nf-test.com)

[![Nextflow](https://img.shields.io/badge/version-%E2%89%A524.10.2-green?style=flat&logo=nextflow&logoColor=white&color=%230DC09D&link=https%3A%2F%2Fnextflow.io)](https://www.nextflow.io/)
[![nf-core template version](https://img.shields.io/badge/nf--core_template-3.3.1-green?style=flat&logo=nfcore&logoColor=white&color=%2324B064&link=https%3A%2F%2Fnf-co.re)](https://github.com/nf-core/tools/releases/tag/3.3.1)
[![run with conda](http://img.shields.io/badge/run%20with-conda-3EB049?labelColor=000000&logo=anaconda)](https://docs.conda.io/en/latest/)
[![run with docker](https://img.shields.io/badge/run%20with-docker-0db7ed?labelColor=000000&logo=docker)](https://www.docker.com/)
[![run with singularity](https://img.shields.io/badge/run%20with-singularity-1d355c.svg?labelColor=000000)](https://sylabs.io/docs/)
[![Launch on Seqera Platform](https://img.shields.io/badge/Launch%20%F0%9F%9A%80-Seqera%20Platform-%234256e7)](https://cloud.seqera.io/launch?pipeline=https://github.com/nf-core/methylseq)

[![Get help on Slack](http://img.shields.io/badge/slack-nf--core%20%23methylseq-4A154B?labelColor=000000&logo=slack)](https://nfcore.slack.com/channels/methylseq)[![Follow on Bluesky](https://img.shields.io/badge/bluesky-%40nf__core-1185fe?labelColor=000000&logo=bluesky)](https://bsky.app/profile/nf-co.re)[![Follow on Mastodon](https://img.shields.io/badge/mastodon-nf__core-6364ff?labelColor=FFFFFF&logo=mastodon)](https://mstdn.science/@nf_core)[![Watch on YouTube](http://img.shields.io/badge/youtube-nf--core-FF0000?labelColor=000000&logo=youtube)](https://www.youtube.com/c/nf-core)

## Introduction

**nf-core/methylseq** is a bioinformatics analysis pipeline used for Methylation (Bisulfite) sequencing data. It pre-processes raw data from FastQ inputs, aligns the reads and performs extensive quality-control on the results.

![nf-core/methylseq metro map](docs/images/4.0.0_metromap.png)

The pipeline is built using [Nextflow](https://www.nextflow.io), a workflow tool to run tasks across multiple compute infrastructures in a very portable manner. It uses Docker / Singularity containers making installation trivial and results highly reproducible.

On release, automated continuous integration tests run the pipeline on a full-sized dataset on the AWS cloud infrastructure. This ensures that the pipeline runs on AWS, has sensible resource allocation defaults set to run on real-world datasets, and permits the persistent storage of results to benchmark between pipeline releases and other analysis sources.The results obtained from the full-sized test can be viewed on the [nf-core website](https://nf-co.re/methylseq/results).

> Read more about **Bisulfite Sequencing & Three-Base Aligners** used in this pipeline [here](./docs/bs-seq-primer.md)

## Pipeline Summary

The pipeline allows you to choose between running either [Bismark](https://github.com/FelixKrueger/Bismark) or [bwa-meth](https://github.com/brentp/bwa-meth) / [MethylDackel](https://github.com/dpryan79/methyldackel).

Choose between workflows by using `--aligner bismark` (default, uses bowtie2 for alignment), `--aligner bismark_hisat` or `--aligner bwameth`. For higher performance, the pipeline can leverage the [Parabricks implementation of bwa-meth (fq2bammeth)](https://docs.nvidia.com/clara/parabricks/latest/documentation/tooldocs/man_fq2bam_meth.html), which implements the baseline tool `bwa-meth` in a performant method using fq2bam (BWA-MEM + GATK) as a backend for processing on GPU. To use this option, include the `gpu` profile along with `--aligner bwameth`.

| Step                                         | Bismark workflow         | bwa-meth workflow     |
| -------------------------------------------- | ------------------------ | --------------------- |
| Generate Reference Genome Index _(optional)_ | Bismark                  | bwa-meth              |
| Merge re-sequenced FastQ files               | cat                      | cat                   |
| Raw data QC                                  | FastQC                   | FastQC                |
| Adapter sequence trimming                    | Trim Galore!             | Trim Galore!          |
| Align Reads                                  | Bismark (bowtie2/hisat2) | bwa-meth              |
| Deduplicate Alignments                       | Bismark                  | Picard MarkDuplicates |
| Extract methylation calls                    | Bismark                  | MethylDackel          |
| Sample report                                | Bismark                  | -                     |
| Summary Report                               | Bismark                  | -                     |
| Alignment QC                                 | Qualimap _(optional)_    | Qualimap _(optional)_ |
| Sample complexity                            | Preseq _(optional)_      | Preseq _(optional)_   |
| Project Report                               | MultiQC                  | MultiQC               |

## Usage

> [!NOTE]
> If you are new to Nextflow and nf-core, please refer to [this page](https://nf-co.re/docs/usage/installation) on how to set-up Nextflow. Make sure to [test your setup](https://nf-co.re/docs/usage/introduction#how-to-run-a-pipeline) with `-profile test` before running the workflow on actual data.

First, prepare a samplesheet with your input data that looks as follows:

`samplesheet.csv`:

```csv
sample,fastq_1,fastq_2,genome
SRR389222_sub1,https://github.com/nf-core/test-datasets/raw/methylseq/testdata/SRR389222_sub1.fastq.gz,,
SRR389222_sub2,https://github.com/nf-core/test-datasets/raw/methylseq/testdata/SRR389222_sub2.fastq.gz,,
SRR389222_sub3,https://github.com/nf-core/test-datasets/raw/methylseq/testdata/SRR389222_sub3.fastq.gz,,
Ecoli_10K_methylated,https://github.com/nf-core/test-datasets/raw/methylseq/testdata/Ecoli_10K_methylated_R1.fastq.gz,https://github.com/nf-core/test-datasets/raw/methylseq/testdata/Ecoli_10K_methylated_R2.fastq.gz,
```

> Each row represents a fastq file (single-end) or a pair of fastq files (paired end).

Now, you can run the pipeline using default parameters as:

```bash
nextflow run nf-core/methylseq --input samplesheet.csv --outdir <OUTDIR> --genome GRCh37 -profile <docker/singularity/podman/shifter/charliecloud/conda/institute>
```

> [!WARNING]
> Please provide pipeline parameters via the CLI or Nextflow `-params-file` option. Custom config files including those provided by the `-c` Nextflow option can be used to provide any configuration _**except for parameters**_; see [docs](https://nf-co.re/docs/usage/getting_started/configuration#custom-configuration-files).

For more details and further functionality, please refer to the [usage documentation](https://nf-co.re/methylseq/usage) and the [parameter documentation](https://nf-co.re/methylseq/parameters).

## Pipeline output

To see the results of an example test run with a full size dataset refer to the [results](https://nf-co.re/methylseq/results) tab on the nf-core website pipeline page.
For more details about the output files and reports, please refer to the [output documentation](https://nf-co.re/methylseq/output).

## Credits

nf-core/methylseq was originally written by Phil Ewels ([@ewels](https://github.com/ewels)), and Sateesh Peri ([@sateeshperi](https://github.com/sateeshperi)) is its active maintainer.

We thank the following people for their extensive assistance in the development of this pipeline:

- Felix Krueger ([@FelixKrueger](https://github.com/FelixKrueger))
- Edmund Miller ([@EMiller88](https://github.com/emiller88))
- Rickard Hammarén ([@Hammarn](https://github.com/Hammarn/))
- Alexander Peltzer ([@apeltzer](https://github.com/apeltzer/))
- Patrick Hüther ([@phue](https://github.com/phue/))
- Maxime U Garcia ([@maxulysse](https://github.com/maxulysse/))

## Contributions and Support

If you would like to contribute to this pipeline, please see the [contributing guidelines](.github/CONTRIBUTING.md).

For further information or help, don't hesitate to get in touch on the [Slack `#methylseq` channel](https://nfcore.slack.com/channels/methylseq) (you can join with [this invite](https://nf-co.re/join/slack)).

## Citations

If you use nf-core/methylseq for your analysis, please cite it using the following doi: [10.5281/zenodo.1343417](https://doi.org/10.5281/zenodo.1343417)

An extensive list of references for the tools used by the pipeline can be found in the [`CITATIONS.md`](CITATIONS.md) file.

You can cite the `nf-core` publication as follows:

> **The nf-core framework for community-curated bioinformatics pipelines.**
>
> Philip Ewels, Alexander Peltzer, Sven Fillinger, Harshil Patel, Johannes Alneberg, Andreas Wilm, Maxime Ulysse Garcia, Paolo Di Tommaso & Sven Nahnsen.
>
> _Nat Biotechnol._ 2020 Feb 13. doi: [10.1038/s41587-020-0439-x](https://dx.doi.org/10.1038/s41587-020-0439-x).


<h1>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/images/nf-core-drugresponseeval_logo_dark.png">
    <img alt="nf-core/drugresponseeval" src="docs/images/nf-core-drugresponseeval_logo_light.png">
  </picture>
</h1>

[![GitHub Actions CI Status](https://github.com/nf-core/drugresponseeval/actions/workflows/ci.yml/badge.svg)](https://github.com/nf-core/drugresponseeval/actions/workflows/ci.yml)
[![GitHub Actions Linting Status](https://github.com/nf-core/drugresponseeval/actions/workflows/linting.yml/badge.svg)](https://github.com/nf-core/drugresponseeval/actions/workflows/linting.yml)[![AWS CI](https://img.shields.io/badge/CI%20tests-full%20size-FF9900?labelColor=000000&logo=Amazon%20AWS)](https://nf-co.re/drugresponseeval/results)[![Cite with Zenodo](http://img.shields.io/badge/DOI-10.5281/zenodo.14779984-1073c8?labelColor=000000)](https://doi.org/10.5281/zenodo.14779984)

[![nf-test](https://img.shields.io/badge/unit_tests-nf--test-337ab7.svg)](https://www.nf-test.com)

[![Nextflow](https://img.shields.io/badge/version-%E2%89%A524.04.2-green?style=flat&logo=nextflow&logoColor=white&color=%230DC09D&link=https%3A%2F%2Fnextflow.io)](https://www.nextflow.io/)
[![nf-core template version](https://img.shields.io/badge/nf--core_template-3.3.1-green?style=flat&logo=nfcore&logoColor=white&color=%2324B064&link=https%3A%2F%2Fnf-co.re)](https://github.com/nf-core/tools/releases/tag/3.3.1)
[![run with conda](http://img.shields.io/badge/run%20with-conda-3EB049?labelColor=000000&logo=anaconda)](https://docs.conda.io/en/latest/)
[![run with docker](https://img.shields.io/badge/run%20with-docker-0db7ed?labelColor=000000&logo=docker)](https://www.docker.com/)
[![run with singularity](https://img.shields.io/badge/run%20with-singularity-1d355c.svg?labelColor=000000)](https://sylabs.io/docs/)
[![Launch on Seqera Platform](https://img.shields.io/badge/Launch%20%F0%9F%9A%80-Seqera%20Platform-%234256e7)](https://cloud.seqera.io/launch?pipeline=https://github.com/nf-core/drugresponseeval)

[![Get help on Slack](http://img.shields.io/badge/slack-nf--core%20%23drugresponseeval-4A154B?labelColor=000000&logo=slack)](https://nfcore.slack.com/channels/drugresponseeval)[![Follow on Bluesky](https://img.shields.io/badge/bluesky-%40nf__core-1185fe?labelColor=000000&logo=bluesky)](https://bsky.app/profile/nf-co.re)[![Follow on Mastodon](https://img.shields.io/badge/mastodon-nf__core-6364ff?labelColor=FFFFFF&logo=mastodon)](https://mstdn.science/@nf_core)[![Watch on YouTube](http://img.shields.io/badge/youtube-nf--core-FF0000?labelColor=000000&logo=youtube)](https://www.youtube.com/c/nf-core)

## Introduction

# ![drevalpy_summary](assets/dreval_summary.svg)

**DrEval** is a bioinformatics framework that includes a PyPI package (drevalpy) and a Nextflow
pipeline (this repo). DrEval ensures that evaluations are statistically sound, biologically
meaningful, and reproducible. DrEval simplifies the implementation of drug response prediction
models, allowing researchers to focus on advancing their modeling innovations by automating
standardized evaluation protocols and preprocessing workflows. With DrEval, hyperparameter
tuning is fair and consistent. With its flexible model interface, DrEval supports any model type,
ranging from statistical models to complex neural networks. By contributing your model to the
DrEval catalog, you can increase your work's exposure, reusability, and transferability.

1. The response data is loaded
2. All models are trained and evaluated in a cross-validation setting
3. For each CV split, the best hyperparameters are determined using a grid search per model
4. The model is trained on the full training set (train & validation) with the best
   hyperparameters to predict the test set
5. If randomization tests are enabled, the model is trained on the full training set with the best
   hyperparameters to predict the randomized test set
6. If robustness tests are enabled, the model is trained N times on the full training set with the
   best hyperparameters
7. Plots are created summarizing the results

For baseline models, no randomization or robustness tests are performed.

## Usage

> [!NOTE]
> If you are new to Nextflow and nf-core, please refer to [this page](https://nf-co.re/docs/usage/installation) on how to set-up Nextflow. Make sure to [test your setup](https://nf-co.re/docs/usage/introduction#how-to-run-a-pipeline) with `-profile test` before running the workflow on actual data.

Now, you can run the pipeline using:

```bash
nextflow run nf-core/drugresponseeval \
   -profile <docker/singularity/.../institute> \
   --models <RandomForest,model2,...> \
   --baselines <NaiveMeanEffectsPredictor,baseline2,...> \
   --dataset_name <CTRPv2|CTRPv1|CCLE|GDSC1|GDSC2|custom_dataset>
```

> [!WARNING]
> Please provide pipeline parameters via the CLI or Nextflow `-params-file` option. Custom config files including those provided by the `-c` Nextflow option can be used to provide any configuration _**except for parameters**_; see [docs](https://nf-co.re/docs/usage/getting_started/configuration#custom-configuration-files).

For more details and further functionality, please refer to the [usage documentation](https://nf-co.re/drugresponseeval/usage) and the [parameter documentation](https://nf-co.re/drugresponseeval/parameters).

## Pipeline output

To see the results of an example test run with a full size dataset refer to the [results](https://nf-co.re/drugresponseeval/results) tab on the nf-core website pipeline page.
For more details about the output files and reports, please refer to the
[output documentation](https://nf-co.re/drugresponseeval/output).

## Credits

nf-core/drugresponseeval was originally written by Judith Bernett (TUM) and Pascal Iversen (FU
Berlin).

We thank the following people for their extensive assistance in the development of this pipeline:

## Contributions and Support

Contributors to nf-core/drugresponseeval and the drevalpy PyPI package:

- [Judith Bernett](https://github.com/JudithBernett) (TUM)
- [Pascal Iversen](https://github.com/PascalIversen) (FU Berlin)
- [Mario Picciani](https://github.com/picciama) (TUM)

If you would like to contribute to this pipeline, please see the [contributing guidelines](.github/CONTRIBUTING.md).

For further information or help, don't hesitate to get in touch on the [Slack `#drugresponseeval` channel](https://nfcore.slack.com/channels/drugresponseeval) (you can join with [this invite](https://nf-co.re/join/slack)).

## Citations

If you use nf-core/drugresponseeval for your analysis, please cite it using the following doi: [10.5281/zenodo.14779984](https://doi.org/10.5281/zenodo.14779984)

> Our corresponding publication is at doi [10.1101/2025.05.26.655288](doi.org/10.1101/2025.05.26.655288)
>
> Bernett, J., Iversen, P., Picciani, M., Wilhelm, M., Baum, K., & List, M. **From Hype to Health Check: Critical Evaluation of Drug Response Prediction Models with DrEval.**
>
> _bioRxiv_, 2025-05.

The underlying data is available at doi: [10.5281/zenodo.12633909](https://doi.org/10.5281/zenodo.12633909).

The underlying python package is drevalpy, availably on [PyPI](https://pypi.org/project/drevalpy/) as standalone, for which we also have an extensive [ReadTheDocs Documentation](https://drevalpy.readthedocs.io/en/latest/).

An extensive list of references for the tools used by the pipeline can be found in the [`CITATIONS.md`](CITATIONS.md) file.

You can cite the `nf-core` publication as follows:

> **The nf-core framework for community-curated bioinformatics pipelines.**
>
> Philip Ewels, Alexander Peltzer, Sven Fillinger, Harshil Patel, Johannes Alneberg, Andreas Wilm, Maxime Ulysse Garcia, Paolo Di Tommaso & Sven Nahnsen.
>
> _Nat Biotechnol._ 2020 Feb 13. doi: [10.1038/s41587-020-0439-x](https://dx.doi.org/10.1038/s41587-020-0439-x).


<h1>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/images/nf-core-oncoanalyser_logo_dark.png">
    <img alt="nf-core/oncoanalyser" src="docs/images/nf-core-oncoanalyser_logo_light.png">
  </picture>
</h1>

[![GitHub Actions CI Status](https://github.com/nf-core/oncoanalyser/actions/workflows/ci.yml/badge.svg)](https://github.com/nf-core/oncoanalyser/actions/workflows/ci.yml)
[![GitHub Actions Linting Status](https://github.com/nf-core/oncoanalyser/actions/workflows/linting.yml/badge.svg)](https://github.com/nf-core/oncoanalyser/actions/workflows/linting.yml)
[![AWS CI](https://img.shields.io/badge/CI%20tests-full%20size-FF9900?labelColor=000000&logo=Amazon%20AWS)](https://nf-co.re/oncoanalyser/results)
[![Cite with Zenodo](http://img.shields.io/badge/DOI-10.5281/zenodo.15189386-1073c8?labelColor=000000)](https://doi.org/10.5281/zenodo.15189386)
[![nf-test](https://img.shields.io/badge/unit_tests-nf--test-337ab7.svg)](https://www.nf-test.com)

[![Nextflow](https://img.shields.io/badge/version-%E2%89%A524.04.2-green?style=flat&logo=nextflow&logoColor=white&color=%230DC09D&link=https%3A%2F%2Fnextflow.io)](https://www.nextflow.io/)
[![nf-core template version](https://img.shields.io/badge/nf--core_template-3.3.1-green?style=flat&logo=nfcore&logoColor=white&color=%2324B064&link=https%3A%2F%2Fnf-co.re)](https://github.com/nf-core/tools/releases/tag/3.3.1)
[![run with conda](http://img.shields.io/badge/run%20with-conda-3EB049?labelColor=000000&logo=anaconda)](https://docs.conda.io/en/latest/)
[![run with docker](https://img.shields.io/badge/run%20with-docker-0db7ed?labelColor=000000&logo=docker)](https://www.docker.com/)
[![run with singularity](https://img.shields.io/badge/run%20with-singularity-1d355c.svg?labelColor=000000)](https://sylabs.io/docs/)
[![Launch on Seqera Platform](https://img.shields.io/badge/Launch%20%F0%9F%9A%80-Seqera%20Platform-%234256e7)](https://cloud.seqera.io/launch?pipeline=https://github.com/nf-core/oncoanalyser)

[![Get help on Slack](http://img.shields.io/badge/slack-nf--core%20%23oncoanalyser-4A154B?labelColor=000000&logo=slack)](https://nfcore.slack.com/channels/oncoanalyser)
[![Follow on Bluesky](https://img.shields.io/badge/bluesky-%40nf__core-1185fe?labelColor=000000&logo=bluesky)](https://bsky.app/profile/nf-co.re)
[![Follow on Mastodon](https://img.shields.io/badge/mastodon-nf__core-6364ff?labelColor=FFFFFF&logo=mastodon)](https://mstdn.science/@nf_core)
[![Watch on YouTube](http://img.shields.io/badge/youtube-nf--core-FF0000?labelColor=000000&logo=youtube)](https://www.youtube.com/c/nf-core)

## Introduction

**nf-core/oncoanalyser** is a Nextflow pipeline for the comprehensive analysis of cancer genomes and transcriptomes
using the [WiGiTS](https://github.com/hartwigmedical/hmftools) toolkit from the Hartwig Medical Foundation. The pipeline
supports a wide range of experimental setups:

- FASTQ, BAM, or CRAM input files
- WGS (whole genome sequencing), WTS (whole transcriptome sequencing), and targeted / panel sequencing (built-in support
  for the [TSO500
  panel](https://sapac.illumina.com/products/by-type/clinical-research-products/trusight-oncology-500.html) with other
  panels and exome requiring [panel reference data
  generation](https://github.com/hartwigmedical/hmftools/blob/master/pipeline/README_TARGETED.md))
- Paired tumor / normal and tumor-only sample setups, donor sample support for further normal subtraction (e.g. for
  patients with bone marrow transplants or other contaminants in the tumor)
- UMI (unique molecular identifier) processing supported for DNA sequencing data
- Most GRCh37 and GRCh38 reference genome builds

## Pipeline overview

<p align="center"><img src="docs/images/oncoanalyser_pipeline.png"></p>

The pipeline mainly uses tools from [WiGiTS](https://github.com/hartwigmedical/hmftools), as well as some external
tools. Due to the limitations of panel data, certain tools (indicated with `*` below) do not run in `targeted` mode.

- Read alignment: [BWA-MEM2](https://github.com/bwa-mem2/bwa-mem2) (DNA), [STAR](https://github.com/alexdobin/STAR) (RNA)
- Read post-processing: [REDUX](https://github.com/hartwigmedical/hmftools/tree/master/redux) (DNA), [Picard MarkDuplicates](https://gatk.broadinstitute.org/hc/en-us/articles/360037052812-MarkDuplicates-Picard) (RNA)
- SNV, MNV, INDEL calling: [SAGE](https://github.com/hartwigmedical/hmftools/tree/master/sage), [PAVE](https://github.com/hartwigmedical/hmftools/tree/master/pave)
- SV calling: [ESVEE](https://github.com/hartwigmedical/hmftools/tree/master/esvee)
- CNV calling: [AMBER](https://github.com/hartwigmedical/hmftools/tree/master/amber), [COBALT](https://github.com/hartwigmedical/hmftools/tree/master/cobalt), [PURPLE](https://github.com/hartwigmedical/hmftools/tree/master/purple)
- SV and driver event interpretation: [LINX](https://github.com/hartwigmedical/hmftools/tree/master/linx)
- RNA transcript analysis: [ISOFOX](https://github.com/hartwigmedical/hmftools/tree/master/isofox)
- Oncoviral detection: [VIRUSbreakend](https://github.com/PapenfussLab/gridss)\*, [VirusInterpreter](https://github.com/hartwigmedical/hmftools/tree/master/virus-interpreter)\*
- Telomere characterisation: [TEAL](https://github.com/hartwigmedical/hmftools/tree/master/teal)\*
- Immune analysis: [LILAC](https://github.com/hartwigmedical/hmftools/tree/master/lilac), [CIDER](https://github.com/hartwigmedical/hmftools/tree/master/cider), [NEO](https://github.com/hartwigmedical/hmftools/tree/master/neo)\*
- Mutational signature fitting: [SIGS](https://github.com/hartwigmedical/hmftools/tree/master/sigs)\*
- HRD prediction: [CHORD](https://github.com/hartwigmedical/hmftools/tree/master/chord)\*
- Tissue of origin prediction: [CUPPA](https://github.com/hartwigmedical/hmftools/tree/master/cuppa)\*
- Pharmacogenomics: [PEACH](https://github.com/hartwigmedical/hmftools/tree/master/peach)
- Summary report: [ORANGE](https://github.com/hartwigmedical/hmftools/tree/master/orange), [linxreport](https://github.com/umccr/linxreport)

## Usage

> [!NOTE]
> If you are new to Nextflow and nf-core, please refer to [this page](https://nf-co.re/docs/usage/installation) on how to set-up Nextflow. Make sure to [test your setup](https://nf-co.re/docs/usage/introduction#how-to-run-a-pipeline) with `-profile test` before running the workflow on actual data.

Create a samplesheet with your inputs (WGS/WTS BAMs in this example):

```csv
group_id,subject_id,sample_id,sample_type,sequence_type,filetype,filepath
PATIENT1_WGTS,PATIENT1,PATIENT1-N,normal,dna,bam,/path/to/PATIENT1-N.dna.bam
PATIENT1_WGTS,PATIENT1,PATIENT1-T,tumor,dna,bam,/path/to/PATIENT1-T.dna.bam
PATIENT1_WGTS,PATIENT1,PATIENT1-T-RNA,tumor,rna,bam,/path/to/PATIENT1-T.rna.bam
```

Launch `oncoanalyser`:

```bash
nextflow run nf-core/oncoanalyser \
  -profile <docker/singularity/.../institute> \
  -revision 2.1.0 \
  --mode <wgts/targeted> \
  --genome <GRCh37_hmf/GRCh38_hmf> \
  --input samplesheet.csv \
  --outdir output/
```

> [!WARNING]
> Please provide pipeline parameters via the CLI or Nextflow `-params-file` option. Custom config files including those provided by the `-c` Nextflow option can be used to provide any configuration _**except for parameters**_; see [docs](https://nf-co.re/docs/usage/getting_started/configuration#custom-configuration-files).

For more details and further functionality, please refer to the [usage documentation](https://nf-co.re/oncoanalyser/usage) and the [parameter documentation](https://nf-co.re/oncoanalyser/parameters).

## Pipeline output

To see the results of an example test run with a full size dataset refer to the [results](https://nf-co.re/oncoanalyser/results) tab on the nf-core website pipeline page.
For more details about the output files and reports, please refer to the
[output documentation](https://nf-co.re/oncoanalyser/output).

## Version information

### Extended support

As `oncoanalyser` is used in clinical settings and subject to accreditation standards in some instances, there is a need
for long-term stability and reliability for feature releases in order to meet operational requirements. This is
accomplished through long-term support of several nominated feature releases, which all receive bug fixes and security
fixes during the period of extended support.

Each release that is given extended support is allocated a separate long-lived git branch with the 'stable' prefix, e.g.
`stable/1.2.x`, `stable/1.5.x`. Feature development otherwise occurs on the `dev` branch with stable releases pushed to
`master`.

Versions nominated to have current long-term support:

- TBD

## Known issues

Please refer to [this page](https://github.com/nf-core/oncoanalyser/issues/177) for details regarding any known issues.

## Credits

The `oncoanalyser` pipeline was written and is maintained by Stephen Watts ([@scwatts](https://github.com/scwatts)) from
the [Genomics Platform
Group](https://mdhs.unimelb.edu.au/centre-for-cancer-research/our-research/genomics-platform-group) at the [University
of Melbourne Centre for Cancer Research](https://mdhs.unimelb.edu.au/centre-for-cancer-research).

We thank the following organisations and people for their extensive assistance in the development of this pipeline,
listed in alphabetical order:

- [Hartwig Medical Foundation
  Australia](https://www.hartwigmedicalfoundation.nl/en/partnerships/hartwig-medical-foundation-australia/)
- Oliver Hofmann

## Contributions and Support

If you would like to contribute to this pipeline, please see the [contributing guidelines](.github/CONTRIBUTING.md).

For further information or help, don't hesitate to get in touch on the [Slack `#oncoanalyser`
channel](https://nfcore.slack.com/channels/oncoanalyser) (you can join with [this invite](https://nf-co.re/join/slack)).

## Citations

You can cite the `oncoanalyser` Zenodo record for a specific version using the following DOI:
[10.5281/zenodo.15189386](https://doi.org/10.5281/zenodo.15189386)

An extensive list of references for the tools used by the pipeline can be found in the [`CITATIONS.md`](CITATIONS.md)
file.

You can cite the `nf-core` publication as follows:

> **The nf-core framework for community-curated bioinformatics pipelines.**
>
> Philip Ewels, Alexander Peltzer, Sven Fillinger, Harshil Patel, Johannes Alneberg, Andreas Wilm, Maxime Ulysse Garcia,
> Paolo Di Tommaso & Sven Nahnsen.
>
> _Nat Biotechnol._ 2020 Feb 13. doi: [10.1038/s41587-020-0439-x](https://dx.doi.org/10.1038/s41587-020-0439-x).

<h1>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/images/nf-core-demo_logo_dark.png">
    <img alt="nf-core/demo" src="docs/images/nf-core-demo_logo_light.png">
  </picture>
</h1>

[![GitHub Actions CI Status](https://github.com/nf-core/demo/actions/workflows/ci.yml/badge.svg)](https://github.com/nf-core/demo/actions/workflows/ci.yml)
[![GitHub Actions Linting Status](https://github.com/nf-core/demo/actions/workflows/linting.yml/badge.svg)](https://github.com/nf-core/demo/actions/workflows/linting.yml)[![AWS CI](https://img.shields.io/badge/CI%20tests-full%20size-FF9900?labelColor=000000&logo=Amazon%20AWS)](https://nf-co.re/demo/results)[![Cite with Zenodo](http://img.shields.io/badge/DOI-10.5281/zenodo.12192442-1073c8?labelColor=000000)](https://doi.org/10.5281/zenodo.12192442)
[![nf-test](https://img.shields.io/badge/unit_tests-nf--test-337ab7.svg)](https://www.nf-test.com)

[![Nextflow](https://img.shields.io/badge/version-%E2%89%A524.04.2-green?style=flat&logo=nextflow&logoColor=white&color=%230DC09D&link=https%3A%2F%2Fnextflow.io)](https://www.nextflow.io/)
[![nf-core template version](https://img.shields.io/badge/nf--core_template-3.3.1-green?style=flat&logo=nfcore&logoColor=white&color=%2324B064&link=https%3A%2F%2Fnf-co.re)](https://github.com/nf-core/tools/releases/tag/3.3.1)
[![run with conda](http://img.shields.io/badge/run%20with-conda-3EB049?labelColor=000000&logo=anaconda)](https://docs.conda.io/en/latest/)
[![run with docker](https://img.shields.io/badge/run%20with-docker-0db7ed?labelColor=000000&logo=docker)](https://www.docker.com/)
[![run with singularity](https://img.shields.io/badge/run%20with-singularity-1d355c.svg?labelColor=000000)](https://sylabs.io/docs/)
[![Launch on Seqera Platform](https://img.shields.io/badge/Launch%20%F0%9F%9A%80-Seqera%20Platform-%234256e7)](https://cloud.seqera.io/launch?pipeline=https://github.com/nf-core/demo)

[![Get help on Slack](http://img.shields.io/badge/slack-nf--core%20%23demo-4A154B?labelColor=000000&logo=slack)](https://nfcore.slack.com/channels/demo)[![Follow on Bluesky](https://img.shields.io/badge/bluesky-%40nf__core-1185fe?labelColor=000000&logo=bluesky)](https://bsky.app/profile/nf-co.re)[![Follow on Mastodon](https://img.shields.io/badge/mastodon-nf__core-6364ff?labelColor=FFFFFF&logo=mastodon)](https://mstdn.science/@nf_core)[![Watch on YouTube](http://img.shields.io/badge/youtube-nf--core-FF0000?labelColor=000000&logo=youtube)](https://www.youtube.com/c/nf-core)

## Introduction

**nf-core/demo** is a simple nf-core style bioinformatics pipeline for workshops and demonstrations. It was created using the nf-core template and is designed to run quickly using small test data files.

![nf-core/demo metro map](docs/images/nf-core-demo-subway.png)

1. Read QC ([`FASTQC`](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/))
2. Adapter and quality trimming ([`SEQTK_TRIM`](https://github.com/lh3/seqtk))
3. Present QC for raw reads ([`MULTIQC`](http://multiqc.info/))

## Usage

> [!NOTE]
> If you are new to Nextflow and nf-core, please refer to [this page](https://nf-co.re/docs/usage/installation) on how to set-up Nextflow. Make sure to [test your setup](https://nf-co.re/docs/usage/introduction#how-to-run-a-pipeline) with `-profile test` before running the workflow on actual data.

First, prepare a samplesheet with your input data that looks as follows:

`samplesheet.csv`:

```csv
sample,fastq_1,fastq_2
SAMPLE1_PE,https://raw.githubusercontent.com/nf-core/test-datasets/viralrecon/illumina/amplicon/sample1_R1.fastq.gz,https://raw.githubusercontent.com/nf-core/test-datasets/viralrecon/illumina/amplicon/sample1_R2.fastq.gz
SAMPLE2_PE,https://raw.githubusercontent.com/nf-core/test-datasets/viralrecon/illumina/amplicon/sample2_R1.fastq.gz,https://raw.githubusercontent.com/nf-core/test-datasets/viralrecon/illumina/amplicon/sample2_R2.fastq.gz
SAMPLE3_SE,https://raw.githubusercontent.com/nf-core/test-datasets/viralrecon/illumina/amplicon/sample1_R1.fastq.gz,
SAMPLE3_SE,https://raw.githubusercontent.com/nf-core/test-datasets/viralrecon/illumina/amplicon/sample2_R1.fastq.gz,
```

Each row represents a fastq file (single-end) or a pair of fastq files (paired end).

Now, you can run the pipeline using:

```bash
nextflow run nf-core/demo \
   -profile <docker/singularity/.../institute> \
   --input samplesheet.csv \
   --outdir <OUTDIR>
```

> [!WARNING]
> Please provide pipeline parameters via the CLI or Nextflow `-params-file` option. Custom config files including those provided by the `-c` Nextflow option can be used to provide any configuration _**except for parameters**_; see [docs](https://nf-co.re/docs/usage/getting_started/configuration#custom-configuration-files).

For more details and further functionality, please refer to the [usage documentation](https://nf-co.re/demo/usage) and the [parameter documentation](https://nf-co.re/demo/parameters).

## Pipeline output

To see the results of an example test run with a full size dataset refer to the [results](https://nf-co.re/demo/results) tab on the nf-core website pipeline page.
For more details about the output files and reports, please refer to the
[output documentation](https://nf-co.re/demo/output).

## Credits

nf-core/demo was originally written by Chris Hakkaart ([@christopher-hakkaart](https://github.com/christopher-hakkaart)).

The pipeline is currently being maintained by the Nextflow community team as well as [Geraldine Van der Auwera](https://github.com/vdauwera) and [Florian Wuennemann](https://github.com/FloWuenne).

<!-- We thank the following people for their extensive assistance in the development of this pipeline: -->

## Contributions and Support

If you would like to contribute to this pipeline, please see the [contributing guidelines](.github/CONTRIBUTING.md).

For further information or help, don't hesitate to get in touch on the [Slack `#demo` channel](https://nfcore.slack.com/channels/demo) (you can join with [this invite](https://nf-co.re/join/slack)).

## Citations

If you use nf-core/demo for your analysis, please cite it using the following doi: [10.5281/zenodo.12192442](https://doi.org/10.5281/zenodo.12192442)

An extensive list of references for the tools used by the pipeline can be found in the [`CITATIONS.md`](CITATIONS.md) file.

You can cite the `nf-core` publication as follows:

> **The nf-core framework for community-curated bioinformatics pipelines.**
>
> Philip Ewels, Alexander Peltzer, Sven Fillinger, Harshil Patel, Johannes Alneberg, Andreas Wilm, Maxime Ulysse Garcia, Paolo Di Tommaso & Sven Nahnsen.
>
> _Nat Biotechnol._ 2020 Feb 13. doi: [10.1038/s41587-020-0439-x](https://dx.doi.org/10.1038/s41587-020-0439-x).

<h1>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/images/nf-core-pathogensurveillance_logo_dark.png">
    <img alt="nf-core/pathogensurveillance" src="docs/images/nf-core-pathogensurveillance_logo_light.png">
  </picture>
</h1>

[![GitHub Actions CI Status](https://github.com/nf-core/pathogensurveillance/actions/workflows/ci.yml/badge.svg)](https://github.com/nf-core/pathogensurveillance/actions/workflows/ci.yml)
[![GitHub Actions Linting Status](https://github.com/nf-core/pathogensurveillance/actions/workflows/linting.yml/badge.svg)](https://github.com/nf-core/pathogensurveillance/actions/workflows/linting.yml)[![AWS CI](https://img.shields.io/badge/CI%20tests-full%20size-FF9900?labelColor=000000&logo=Amazon%20AWS)](https://nf-co.re/pathogensurveillance/results)[![Cite with Zenodo](http://img.shields.io/badge/DOI-10.5281/zenodo.XXXXXXX-1073c8?labelColor=000000)](https://doi.org/10.5281/zenodo.XXXXXXX)
[![nf-test](https://img.shields.io/badge/unit_tests-nf--test-337ab7.svg)](https://www.nf-test.com)

[![Nextflow](https://img.shields.io/badge/version-%E2%89%A524.04.2-green?style=flat&logo=nextflow&logoColor=white&color=%230DC09D&link=https%3A%2F%2Fnextflow.io)](https://www.nextflow.io/)
[![nf-core template version](https://img.shields.io/badge/nf--core_template-3.3.1-green?style=flat&logo=nfcore&logoColor=white&color=%2324B064&link=https%3A%2F%2Fnf-co.re)](https://github.com/nf-core/tools/releases/tag/3.3.1)
[![run with conda](http://img.shields.io/badge/run%20with-conda-3EB049?labelColor=000000&logo=anaconda)](https://docs.conda.io/en/latest/)
[![run with docker](https://img.shields.io/badge/run%20with-docker-0db7ed?labelColor=000000&logo=docker)](https://www.docker.com/)
[![run with singularity](https://img.shields.io/badge/run%20with-singularity-1d355c.svg?labelColor=000000)](https://sylabs.io/docs/)
[![Launch on Seqera Platform](https://img.shields.io/badge/Launch%20%F0%9F%9A%80-Seqera%20Platform-%234256e7)](https://cloud.seqera.io/launch?pipeline=https://github.com/nf-core/pathogensurveillance)

[![Get help on Slack](http://img.shields.io/badge/slack-nf--core%20%23pathogensurveillance-4A154B?labelColor=000000&logo=slack)](https://nfcore.slack.com/channels/pathogensurveillance)[![Follow on Bluesky](https://img.shields.io/badge/bluesky-%40nf__core-1185fe?labelColor=000000&logo=bluesky)](https://bsky.app/profile/nf-co.re)[![Follow on Mastodon](https://img.shields.io/badge/mastodon-nf__core-6364ff?labelColor=FFFFFF&logo=mastodon)](https://mstdn.science/@nf_core)[![Watch on YouTube](http://img.shields.io/badge/youtube-nf--core-FF0000?labelColor=000000&logo=youtube)](https://www.youtube.com/c/nf-core)

## Introduction

**nf-core/pathogensurveillance** is a population genomics pipeline for pathogen identification, variant detection, and biosurveillance.
The pipeline accepts paths to raw reads for one or more organisms and creates reports in the form of an interactive HTML document.
Significant features include the ability to analyze unidentified eukaryotic and prokaryotic samples, creation of reports for multiple user-defined groupings of samples, automated discovery and downloading of reference assemblies from [NCBI RefSeq](https://www.ncbi.nlm.nih.gov/refseq/), and rapid initial identification based on k-mer sketches followed by a more robust multi gene phylogeny and SNP-based phylogeny.

The pipeline is built using [Nextflow](https://www.nextflow.io), a workflow tool to run tasks across multiple compute infrastructures in a very portable manner.
It uses Docker/Singularity/Conda to make installation trivial and results highly reproducible.
The [Nextflow DSL2](https://www.nextflow.io/docs/latest/dsl2.html) implementation of this pipeline uses one container per process which makes it much easier to maintain and update software dependencies.
Where appropriate, these processes have been submitted to and installed from [nf-core/modules](https://github.com/nf-core/modules) in order to make them available to all nf-core pipelines, and to everyone within the Nextflow community!

On release, automated continuous integration tests run the pipeline on a full-sized dataset on the AWS cloud infrastructure.
This ensures that the pipeline runs on AWS, has sensible resource allocation defaults set to run on real-world data sets, and permits the persistent storage of results to benchmark between pipeline releases and other analysis sources. The results obtained from the full-sized test can be viewed on the [nf-core website](https://nf-co.re/pathogensurveillance/results).

## Pipeline summary

![](docs/images/pipeline_diagram.png)

## Quick start guide

> [!NOTE]
> If you are new to Nextflow and nf-core, please refer to [this page](https://nf-co.re/docs/usage/installation) on how to set-up Nextflow. Make sure to [test your setup](https://nf-co.re/docs/usage/introduction#how-to-run-a-pipeline) with `-profile test` before running the workflow on actual data.

Note that some form of configuration will be needed so that Nextflow knows how to fetch the required software.
This is usually done in the form of a config profile.
You can chain multiple config profiles in a comma-separated string.
In most cases you will include one profile that defines a tool to reproducibly install and use software needed by the pipeline.
This is typically one of `docker`, `singularity`, or `conda`.
Ideally `conda` should not be used unless `docker` or `singularity` cannot be used.

Profiles can also be used to store parameters for the pipeline, such as input data and pipeline options.
Before using you own data, consider trying out a small example dataset included with the pipeline as a profile.
Available test dataset profiles include:

- `test`: Test profile of 1 small genome used to run the pipeline as fast as possible for testing purposes.
- `test_serratia`: Test profile of 10 serratia isolates from Williams et al. 2022 (https://doi.org/10.1038/s41467-022-32929-2)
- `test_bordetella`: Test profile of 5 Bordetella pertussis isolates sequenced with with Illumina and Nanopore from Wagner et al. 2023
- `test_salmonella`: Test profile of 5 salmonella isolates from Hawkey et al. 2024 (https://doi.org/10.1038/s41467-024-54418-4)
- `test_boxwood_blight`: Test profile of 5 samples of the boxwood blight fungus Cylindrocladium buxicola from LeBlanc et al. 2020 (https://doi.org/10.1094/PHYTO-06-20-0219-FI)
- `test_mycobacteroides`: Test profile of 5 Mycobacteroides abscessus samples from Bronson et al. 2021 (https://doi.org/10.1038/s41467-021-25484-9)
- `test_bacteria`: Test profile of 10 mixed bacteria from various sources
- `test_klebsiella`: Test profile of 10 K. pneumoniae and related species from Holt et al. 2015 (https://doi.org/10.1073/pnas.1501049112)
- `test_small_genomes`: Test profile consisting of 6 samples from species with small genomes from various sources.

Adding `_full` to the end of any of these profiles will run a larger (often much larger) version of these datasets.

For example, you can run the `test_bacteria` profile with the `docker` profile:

```bash
nextflow run nf-core/pathogensurveillance -profile docker,test_bacteria -resume --outdir test_output
```

You can see the samplesheets used in these profiles here:

https://github.com/nf-core/test-datasets/tree/pathogensurveillance

To run your own input data, prepare a samplesheet as described in the [usage documentation](docs/usage/#samplesheet-input) section below and run the following command:

```bash
nextflow run nf-core/pathogensurveillance -profile <REPLACE WITH RUN TOOL> -resume --input <REPLACE WITH TSV/CSV> --outdir <REPLACE WITH OUTPUT PATH>
```

Where:

- `<REPLACE WITH RUN TOOL>` is one of `docker`, `singularity`, or `conda`
- `<REPLACE WITH TSV/CSV>` is the path to the input samplesheet
- `<REPLACE WITH OUTPUT PATH>` is the path to where to save the output

## Documentation

For more details and further functionality, please refer to the [usage documentation](https://nf-co.re/pathogensurveillance/usage) and the [parameter documentation](https://nf-co.re/pathogensurveillance/parameters).
To see the results of an example test run with a full size dataset refer to the [results](https://nf-co.re/pathogensurveillance/results) tab on the nf-core website pipeline page.
For more details about the output files and reports, please refer to the [output documentation](https://nf-co.re/pathogensurveillance/output).

## Credits

The following people contributed to the pipeline: Zachary S.L. Foster, Martha Sudermann, Camilo Parada-Rojas, Logan K. Blair, Fernanda I. Bocardo, Ricardo Alcalá-Briseño, Hung Phan, Nicholas C. Cauldron, Alexandra J. Weisberg, Jeﬀ H. Chang, and Niklaus J. Grünwald.

## Funding

This work was supported by grants from USDA ARS (2072-22000-045-000-D) to NJG, USDA NIFA (2021-67021-34433; 2023-67013-39918) to JHC and NJG, as well as USDAR ARS NPDRS and FNRI and USDA APHIS to NJG.

## Contributions and Support

If you would like to contribute to this pipeline, please see the [contributing guidelines](.github/CONTRIBUTING.md).

For further information or help, don't hesitate to get in touch on the [Slack `#pathogensurveillance` channel](https://nfcore.slack.com/channels/pathogensurveillance) (you can join with [this invite](https://nf-co.re/join/slack)).

## Citations

<!-- TODO nf-core: Add citation for pipeline after first release. Uncomment lines below and update Zenodo doi and badge at the top of this file. -->
<!-- If you use nf-core/pathogensurveillance for your analysis, please cite it using the following doi: [10.5281/zenodo.XXXXXX](https://doi.org/10.5281/zenodo.XXXXXX) -->

<!-- TODO nf-core: Add bibliography of tools and data used in your pipeline -->

An extensive list of references for the tools used by the pipeline can be found in the [`CITATIONS.md`](CITATIONS.md) file.

You can cite the `nf-core` publication as follows:

> **The nf-core framework for community-curated bioinformatics pipelines.**
>
> Philip Ewels, Alexander Peltzer, Sven Fillinger, Harshil Patel, Johannes Alneberg, Andreas Wilm, Maxime Ulysse Garcia, Paolo Di Tommaso & Sven Nahnsen.
>
> _Nat Biotechnol._ 2020 Feb 13. doi: [10.1038/s41587-020-0439-x](https://dx.doi.org/10.1038/s41587-020-0439-x).

<picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/images/combined_logos_dark.png">
    <img alt="Logos of University of Oregon and USAD" src="docs/images/combined_logos_light.png">
</picture>

<h1>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/images/nf-core-raredisease_logo_dark.png">
    <img alt="nf-core/raredisease" src="docs/images/nf-core-raredisease_logo_light.png">
  </picture>
</h1>

[![GitHub Actions CI Status](https://github.com/nf-core/raredisease/actions/workflows/ci.yml/badge.svg)](https://github.com/nf-core/raredisease/actions/workflows/ci.yml)

[![GitHub Actions Linting Status](https://github.com/nf-core/raredisease/actions/workflows/linting.yml/badge.svg)](https://github.com/nf-core/raredisease/actions/workflows/linting.yml)[![AWS CI](https://img.shields.io/badge/CI%20tests-full%20size-FF9900?labelColor=000000&logo=Amazon%20AWS)](https://nf-co.re/raredisease/results)[![Cite with Zenodo](http://img.shields.io/badge/DOI-10.5281/zenodo.7995798-1073c8?labelColor=000000)](https://doi.org/10.5281/zenodo.7995798)
[![nf-test](https://img.shields.io/badge/unit_tests-nf--test-337ab7.svg)](https://www.nf-test.com)
[![GitHub Actions Linting Status](https://github.com/nf-core/raredisease/actions/workflows/linting.yml/badge.svg)](https://github.com/nf-core/raredisease/actions/workflows/linting.yml)[![AWS CI](https://img.shields.io/badge/CI%20tests-full%20size-FF9900?labelColor=000000&logo=Amazon%20AWS)](https://nf-co.re/raredisease/results)[![Cite with Zenodo](http://img.shields.io/badge/DOI-10.5281/zenodo.7995798-1073c8?labelColor=000000)](https://doi.org/10.5281/zenodo.7995798)

[![Nextflow](https://img.shields.io/badge/nextflow%20DSL2-%E2%89%A524.04.2-23aa62.svg)](https://www.nextflow.io/)
[![nf-core template version](https://img.shields.io/badge/nf--core_template-3.3.1-green?style=flat&logo=nfcore&logoColor=white&color=%2324B064&link=https%3A%2F%2Fnf-co.re)](https://github.com/nf-core/tools/releases/tag/3.3.1)
[![run with conda](http://img.shields.io/badge/run%20with-conda-3EB049?labelColor=000000&logo=anaconda)](https://docs.conda.io/en/latest/)
[![run with docker](https://img.shields.io/badge/run%20with-docker-0db7ed?labelColor=000000&logo=docker)](https://www.docker.com/)
[![run with singularity](https://img.shields.io/badge/run%20with-singularity-1d355c.svg?labelColor=000000)](https://sylabs.io/docs/)
[![Launch on Seqera Platform](https://img.shields.io/badge/Launch%20%F0%9F%9A%80-Seqera%20Platform-%234256e7)](https://cloud.seqera.io/launch?pipeline=https://github.com/nf-core/raredisease)

[![Get help on Slack](http://img.shields.io/badge/slack-nf--core%20%23raredisease-4A154B?labelColor=000000&logo=slack)](https://nfcore.slack.com/channels/raredisease)[![Follow on Bluesky](https://img.shields.io/badge/bluesky-%40nf__core-1185fe?labelColor=000000&logo=bluesky)](https://bsky.app/profile/nf-co.re)[![Follow on Mastodon](https://img.shields.io/badge/mastodon-nf__core-6364ff?labelColor=FFFFFF&logo=mastodon)](https://mstdn.science/@nf_core)[![Watch on YouTube](http://img.shields.io/badge/youtube-nf--core-FF0000?labelColor=000000&logo=youtube)](https://www.youtube.com/c/nf-core)

#### TOC

- [Introduction](#introduction)
- [Pipeline summary](#pipeline-summary)
- [Usage](#usage)
- [Pipeline output](#pipeline-output)
- [Credits](#credits)
- [Contributions and Support](#contributions-and-support)
- [Citations](#citations)

## Introduction

**nf-core/raredisease** is a best-practice bioinformatic pipeline for calling and scoring variants from WGS/WES data from rare disease patients. This pipeline is heavily inspired by [MIP](https://github.com/Clinical-Genomics/MIP).

> [!NOTE]
> Right now, we only support paired-end data from Illumina. If you've got other types of data and the pipeline doesn't work for you, just open an issue. We'd be happy to chat about a solution.

The pipeline is built using [Nextflow](https://www.nextflow.io), a workflow tool to run tasks across multiple compute infrastructures in a very portable manner. It uses Docker/Singularity containers making installation trivial and results highly reproducible. The [Nextflow DSL2](https://www.nextflow.io/docs/latest/dsl2.html) implementation of this pipeline uses one container per process which makes it much easier to maintain and update software dependencies. Where possible, these processes have been submitted to and installed from [nf-core/modules](https://github.com/nf-core/modules) in order to make them available to all nf-core pipelines, and to everyone within the Nextflow community!

On release, automated continuous integration tests run the pipeline on a full-sized dataset on the AWS cloud infrastructure. This ensures that the pipeline runs on AWS, has sensible resource allocation defaults set to run on real-world datasets, and permits the persistent storage of results to benchmark between pipeline releases and other analysis sources. The results obtained from the full-sized test can be viewed on the [nf-core website](https://nf-co.re/raredisease/results).

## Pipeline summary

  <picture align="center">
    <source media="(prefers-color-scheme: dark)" srcset="docs/images/raredisease_metromap_dark.png">
    <img alt="nf-core/raredisease workflow" src="docs/images/raredisease_metromap_light.png">
  </picture>

**1. Metrics:**

- [FastQC](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/)
- [Mosdepth](https://github.com/brentp/mosdepth)
- [MultiQC](http://multiqc.info/)
- [Picard's CollectMutipleMetrics, CollectHsMetrics, and CollectWgsMetrics](https://broadinstitute.github.io/picard/)
- [Qualimap](http://qualimap.conesalab.org/)
- [Sentieon's WgsMetricsAlgo](https://support.sentieon.com/manual/usages/general/)
- [TIDDIT's cov](https://github.com/J35P312/)
- [VerifyBamID2](https://github.com/Griffan/VerifyBamID)

**2. Alignment:**

- [Bwa-mem2](https://github.com/bwa-mem2/bwa-mem2)
- [BWA-MEME](https://github.com/kaist-ina/BWA-MEME)
- [BWA](https://github.com/lh3/bwa)
- [Sentieon DNAseq](https://support.sentieon.com/manual/DNAseq_usage/dnaseq/)

**3. Variant calling - SNV:**

- [DeepVariant](https://github.com/google/deepvariant)
- [Sentieon DNAscope](https://support.sentieon.com/manual/DNAscope_usage/dnascope/)

**4. Variant calling - SV:**

- [Manta](https://github.com/Illumina/manta)
- [TIDDIT's sv](https://github.com/SciLifeLab/TIDDIT)
- Copy number variant calling:
  - [CNVnator](https://github.com/abyzovlab/CNVnator)
  - [GATK GermlineCNVCaller](https://github.com/broadinstitute/gatk)

**5. Annotation - SNV:**

- [bcftools roh](https://samtools.github.io/bcftools/bcftools.html#roh)
- [vcfanno](https://github.com/brentp/vcfanno)
- [CADD](https://cadd.gs.washington.edu/)
- [VEP](https://www.ensembl.org/info/docs/tools/vep/index.html)
- [UPD](https://github.com/bjhall/upd)
- [Chromograph](https://github.com/Clinical-Genomics/chromograph)

**6. Annotation - SV:**

- [SVDB query](https://github.com/J35P312/SVDB#Query)
- [VEP](https://www.ensembl.org/info/docs/tools/vep/index.html)

**7. Mitochondrial analysis:**

- [Alignment and variant calling - GATK Mitochondrial short variant discovery pipeline ](https://gatk.broadinstitute.org/hc/en-us/articles/4403870837275-Mitochondrial-short-variant-discovery-SNVs-Indels-)
- [eKLIPse](https://github.com/dooguypapua/eKLIPse/tree/master)
- Annotation:
  - [HaploGrep2](https://github.com/seppinho/haplogrep-cmd)
  - [Hmtnote](https://github.com/robertopreste/HmtNote)
  - [vcfanno](https://github.com/brentp/vcfanno)
  - [CADD](https://cadd.gs.washington.edu/)
  - [VEP](https://www.ensembl.org/info/docs/tools/vep/index.html)

**8. Variant calling - repeat expansions:**

- [Expansion Hunter](https://github.com/Illumina/ExpansionHunter)
- [Stranger](https://github.com/Clinical-Genomics/stranger)

**9. Variant calling - mobile elements:**

- [RetroSeq](https://github.com/tk2/RetroSeq)

**10. Rank variants - SV and SNV:**

- [GENMOD](https://github.com/Clinical-Genomics/genmod)

**11. Variant evaluation:**

- [RTG Tools](https://github.com/RealTimeGenomics/rtg-tools)

Note that it is possible to include/exclude certain tools or steps.

## Usage

> [!NOTE]
> If you are new to Nextflow and nf-core, please refer to [this page](https://nf-co.re/docs/usage/installation) on how to set-up Nextflow. Make sure to [test your setup](https://nf-co.re/docs/usage/introduction#how-to-run-a-pipeline) with `-profile test` before running the workflow on actual data.

First, prepare a samplesheet with your input data that looks as follows:

`samplesheet.csv`:

```csv
sample,lane,fastq_1,fastq_2,sex,phenotype,paternal_id,maternal_id,case_id
hugelymodelbat,1,reads_1.fastq.gz,reads_2.fastq.gz,1,2,,,justhusky
```

Each row represents a pair of fastq files (paired end).

Second, ensure that you have defined the path to reference files and parameters required for the type of analysis that you want to perform. More information about this can be found [here](https://github.com/nf-core/raredisease/blob/dev/docs/usage.md).

Now, you can run the pipeline using:

```bash
nextflow run nf-core/raredisease \
   -profile <docker/singularity/podman/shifter/charliecloud/conda/institute> \
   --input samplesheet.csv \
   --outdir <OUTDIR>
```

> [!WARNING]
> Please provide pipeline parameters via the CLI or Nextflow `-params-file` option. Custom config files including those provided by the `-c` Nextflow option can be used to provide any configuration _**except for parameters**_; see [docs](https://nf-co.re/docs/usage/getting_started/configuration#custom-configuration-files).

For more details and further functionality, please refer to the [usage documentation](https://nf-co.re/raredisease/usage) and the [parameter documentation](https://nf-co.re/raredisease/parameters).

## Pipeline output

For more details about the output files and reports, please refer to the
[output documentation](https://nf-co.re/raredisease/output).

## Credits

nf-core/raredisease was written in a collaboration between the Clinical Genomics nodes in Sweden, with major contributions from [Ramprasad Neethiraj](https://github.com/ramprasadn), [Anders Jemt](https://github.com/jemten), [Lucia Pena Perez](https://github.com/Lucpen), and [Mei Wu](https://github.com/projectoriented) at Clinical Genomics Stockholm.

Additional contributors were [Sima Rahimi](https://github.com/sima-r), [Gwenna Breton](https://github.com/Gwennid) and [Emma Västerviga](https://github.com/EmmaCAndersson) (Clinical Genomics Gothenburg); [Halfdan Rydbeck](https://github.com/hrydbeck) and [Lauri Mesilaakso](https://github.com/ljmesi) (Clinical Genomics Linköping); [Subazini Thankaswamy Kosalai](https://github.com/sysbiocoder) (Clinical Genomics Örebro); [Annick Renevey](https://github.com/rannick), [Peter Pruisscher](https://github.com/peterpru) and [Eva Caceres](https://github.com/fevac) (Clinical Genomics Stockholm); [Ryan Kennedy](https://github.com/ryanjameskennedy) (Clinical Genomics Lund); [Anders Sune Pedersen](https://github.com/asp8200) (Danish National Genome Center) and [Lucas Taniguti](https://github.com/lmtani).

We thank the nf-core community for their extensive assistance in the development of this pipeline.

## Contributions and Support

If you would like to contribute to this pipeline, please see the [contributing guidelines](.github/CONTRIBUTING.md).

For further information or help, don't hesitate to get in touch on the [Slack `#raredisease` channel](https://nfcore.slack.com/channels/raredisease) (you can join with [this invite](https://nf-co.re/join/slack)).

## Citations

If you use nf-core/raredisease for your analysis, please cite it using the following doi: [10.5281/zenodo.7995798](https://doi.org/10.5281/zenodo.7995798)

An extensive list of references for the tools used by the pipeline can be found in the [`CITATIONS.md`](CITATIONS.md) file.

You can cite the `nf-core` publication as follows:

> **The nf-core framework for community-curated bioinformatics pipelines.**
>
> Philip Ewels, Alexander Peltzer, Sven Fillinger, Harshil Patel, Johannes Alneberg, Andreas Wilm, Maxime Ulysse Garcia, Paolo Di Tommaso & Sven Nahnsen.
>
> _Nat Biotechnol._ 2020 Feb 13. doi: [10.1038/s41587-020-0439-x](https://dx.doi.org/10.1038/s41587-020-0439-x).

You can read more about MIP's use in healthcare in,

> Stranneheim H, Lagerstedt-Robinson K, Magnusson M, et al. Integration of whole genome sequencing into a healthcare setting: high diagnostic rates across multiple clinical entities in 3219 rare disease patients. Genome Med. 2021;13(1):40. doi:10.1186/s13073-021-00855-5


<h1>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/images/nf-core-pixelator_logo_dark.png">
    <img alt="nf-core/pixelator" src="docs/images/nf-core-pixelator_logo_light.png">
  </picture>
</h1>

[![GitHub Actions CI Status](https://github.com/nf-core/pixelator/actions/workflows/ci.yml/badge.svg)](https://github.com/nf-core/pixelator/actions/workflows/ci.yml)
[![GitHub Actions Linting Status](https://github.com/nf-core/pixelator/actions/workflows/linting.yml/badge.svg)](https://github.com/nf-core/pixelator/actions/workflows/linting.yml)
[![AWS CI](https://img.shields.io/badge/CI%20tests-full%20size-FF9900?labelColor=000000&logo=Amazon%20AWS)](https://nf-co.re/pixelator/results)
[![Cite with Zenodo](http://img.shields.io/badge/DOI-10.5281/zenodo.10015112-1073c8?labelColor=000000)](https://doi.org/10.5281/zenodo.10015112)
[![nf-test](https://img.shields.io/badge/unit_tests-nf--test-337ab7.svg)](https://www.nf-test.com)

[![Nextflow](https://img.shields.io/badge/nextflow%20DSL2-%E2%89%A524.04.2-23aa62.svg)](https://www.nextflow.io/)
[![run with conda](http://img.shields.io/badge/run%20with-conda-3EB049?labelColor=000000&logo=anaconda)](https://docs.conda.io/en/latest/)
[![run with docker](https://img.shields.io/badge/run%20with-docker-0db7ed?labelColor=000000&logo=docker)](https://www.docker.com/)
[![run with singularity](https://img.shields.io/badge/run%20with-singularity-1d355c.svg?labelColor=000000)](https://sylabs.io/docs/)
[![Launch on Seqera Platform](https://img.shields.io/badge/Launch%20%F0%9F%9A%80-Seqera%20Platform-%234256e7)](https://cloud.seqera.io/launch?pipeline=https://github.com/nf-core/pixelator)

[![Get help on Slack](http://img.shields.io/badge/slack-nf--core%20%23pixelator-4A154B?labelColor=000000&logo=slack)](https://nfcore.slack.com/channels/pixelator)[![Follow on Twitter](http://img.shields.io/badge/twitter-%40nf__core-1DA1F2?labelColor=000000&logo=twitter)](https://twitter.com/nf_core)[![Follow on Mastodon](https://img.shields.io/badge/mastodon-nf__core-6364ff?labelColor=FFFFFF&logo=mastodon)](https://mstdn.science/@nf_core)[![Watch on YouTube](http://img.shields.io/badge/youtube-nf--core-FF0000?labelColor=000000&logo=youtube)](https://www.youtube.com/c/nf-core)

## Introduction

**nf-core/pixelator** is a bioinformatics best-practice analysis pipeline for analysis of data from the
Molecular Pixelation (MPX) and Proximity Network (PNA) assays. It takes a samplesheet as input and will process your data
using `pixelator` to produce a PXL file containing single-cell protein abundance and protein interactomics data.

![](./docs/images/nf-core-pixelator-metromap.svg)

Depending on the input data the pipeline will run different steps.

For PNA data, the pipeline will run the following steps:

1. Do quality control checks of input reads and build amplicons ([`pixelator single-cell-pna amplicon`](https://github.com/PixelgenTechnologies/pixelator))
2. Create groups of amplicons based on their marker assignments ([`pixelator single-cell-pna demux`](https://github.com/PixelgenTechnologies/pixelator))
3. Derive original molecules to use as edge list downstream by error correcting, and counting input amplicons ([`pixelator single-cell-pna collapse`](https://github.com/PixelgenTechnologies/pixelator))
4. Compute the components of the graph from the edge list in order to create putative cells ([`pixelator single-cell-pna graph`](https://github.com/PixelgenTechnologies/pixelator))
5. Analyze the spatial information in the cell graphs ([`pixelator single-cell-pna analysis`](https://github.com/PixelgenTechnologies/pixelator))
6. Generate 3D graph layouts for visualization of cells ([`pixelator single-cell-pna layout`](https://github.com/PixelgenTechnologies/pixelator))
7. Report generation ([`pixelator single-cell-pna report`](https://github.com/PixelgenTechnologies/pixelator))

For MPX data, the pipeline will run the following steps:

1. Build an amplicons from the input reads ([`pixelator single-cell-mpx amplicon`](https://github.com/PixelgenTechnologies/pixelator))
2. Read QC and filtering, correctness of the pixel binding sequence sequences ([`pixelator single-cell-mpx preqc | pixelator adapterqc`](https://github.com/PixelgenTechnologies/pixelator))
3. Assign a marker (barcode) to each read ([`pixelator single-cell-mpx demux`](https://github.com/PixelgenTechnologies/pixelator))
4. Error correction, duplicate removal, compute read counts ([`pixelator single-cell-mpx collapse`](https://github.com/PixelgenTechnologies/pixelator))
5. Compute the components of the graph from the edge list in order to create putative cells ([`pixelator single-cell-mpx graph`](https://github.com/PixelgenTechnologies/pixelator))
6. Call and annotate cells ([`pixelator single-cell-mpx annotate`](https://github.com/PixelgenTechnologies/pixelator))
7. Analyze the cells for polarization and colocalization ([`pixelator single-cell-mpx analysis`](https://github.com/PixelgenTechnologies/pixelator))
8. Generate 3D graph layouts for visualization of cells ([`pixelator single-cell-mpx layout`](https://github.com/PixelgenTechnologies/pixelator))
9. Report generation ([`pixelator single-cell-mpx report`](https://github.com/PixelgenTechnologies/pixelator))

> [!WARNING]
> Since Nextflow 23.07.0-edge, Nextflow no longer mounts the host's home directory when using Apptainer or Singularity.
> This causes issues in some dependencies. As a workaround, you can revert to the old behavior by setting the environment variable
> `NXF_APPTAINER_HOME_MOUNT` or `NXF_SINGULARITY_HOME_MOUNT` to `true` in the machine from which you launch the pipeline.

## Usage

> [!NOTE]
> If you are new to Nextflow and nf-core, please refer to [this page](https://nf-co.re/docs/usage/installation) on how to set-up Nextflow. Make sure to [test your setup](https://nf-co.re/docs/usage/introduction#how-to-run-a-pipeline) with `-profile test` before running the workflow on actual data.

First, prepare a samplesheet with your input data that looks as follows (the exact values you need to input depend on the design and panel you are using):

`samplesheet.csv`:

```csv
sample,design,panel,fastq_1,fastq_2
sample1,pna-2,proxiome-immuno-155,sample1_R1_001.fastq.gz,sample1_R2_001.fastq.gz
```

Each row represents a sample and gives the design, a panel file and the input fastq files.

Now, you can run the pipeline using:

```bash
nextflow run nf-core/pixelator \
   -profile <docker/singularity/.../institute> \
   --input samplesheet.csv \
   --outdir <OUTDIR>
```

> [!WARNING]
> This version of the pipeline does not support conda environments, due to issues with upstream dependencies.
> This means you cannot use the `conda` and `mamba` profiles. Please use `docker` or `singularity` instead.
> We hope to add support for conda environments in the future.

> [!WARNING]
> Please provide pipeline parameters via the CLI or Nextflow `-params-file` option. Custom config files including those provided by the `-c` Nextflow option can be used to provide any configuration _**except for parameters**_; see [docs](https://nf-co.re/docs/usage/getting_started/configuration#custom-configuration-files).

For more details and further functionality, please refer to the [usage documentation](https://nf-co.re/pixelator/usage) and the [parameter documentation](https://nf-co.re/pixelator/parameters).

## Pipeline output

To see the results of an example test run with a full size dataset refer to the [results](https://nf-co.re/pixelator/results) tab on the nf-core website pipeline page.
For more details about the output files and reports, please refer to the
[output documentation](https://nf-co.re/pixelator/output).

## Credits

nf-core/pixelator was originally written for [Pixelgen Technologies AB](https://www.pixelgen.com/) by:

- Florian De Temmerman
- Johan Dahlberg
- Alvaro Martinez Barrio

## Contributions and Support

If you would like to contribute to this pipeline, please see the [contributing guidelines](.github/CONTRIBUTING.md).

For further information or help, don't hesitate to get in touch on the [Slack `#pixelator` channel](https://nfcore.slack.com/channels/pixelator) (you can join with [this invite](https://nf-co.re/join/slack)).

## Citations

If you use nf-core/pixelator for your analysis, please cite it using the following doi: [10.5281/zenodo.10015112](https://doi.org/10.5281/zenodo.10015112)

An extensive list of references for the tools used by the pipeline can be found in the [`CITATIONS.md`](CITATIONS.md) file.

You can cite the `nf-core` publication as follows:

> **The nf-core framework for community-curated bioinformatics pipelines.**
>
> Philip Ewels, Alexander Peltzer, Sven Fillinger, Harshil Patel, Johannes Alneberg, Andreas Wilm, Maxime Ulysse Garcia, Paolo Di Tommaso & Sven Nahnsen.
>
> _Nat Biotechnol._ 2020 Feb 13. doi: [10.1038/s41587-020-0439-x](https://dx.doi.org/10.1038/s41587-020-0439-x).

You can cite the molecular pixelation technology as follows:

> **Molecular pixelation: spatial proteomics of single cells by sequencing.**
>
> Filip Karlsson, Tomasz Kallas, Divya Thiagarajan, Max Karlsson, Maud Schweitzer, Jose Fernandez Navarro, Louise Leijonancker, Sylvain Geny, Erik Pettersson, Jan Rhomberg-Kauert, Ludvig Larsson, Hanna van Ooijen, Stefan Petkov, Marcela González-Granillo, Jessica Bunz, Johan Dahlberg, Michele Simonetti, Prajakta Sathe, Petter Brodin, Alvaro Martinez Barrio & Simon Fredriksson
>
> _Nat Methods._ 2024 May 08. doi: [10.1038/s41592-024-02268-9](https://doi.org/10.1038/s41592-024-02268-9)


<h1>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/images/nf-core-createtaxdb_logo_dark_tax.png">
    <img alt="nf-core/createtaxdb" src="docs/images/nf-core-createtaxdb_logo_light_tax.png">
  </picture>
</h1>

[![GitHub Actions CI Status](https://github.com/nf-core/createtaxdb/actions/workflows/ci.yml/badge.svg)](https://github.com/nf-core/createtaxdb/actions/workflows/ci.yml)
[![GitHub Actions Linting Status](https://github.com/nf-core/createtaxdb/actions/workflows/linting.yml/badge.svg)](https://github.com/nf-core/createtaxdb/actions/workflows/linting.yml)[![AWS CI](https://img.shields.io/badge/CI%20tests-full%20size-FF9900?labelColor=000000&logo=Amazon%20AWS)](https://nf-co.re/createtaxdb/results)[![Cite with Zenodo](http://img.shields.io/badge/DOI-10.5281/zenodo.XXXXXXX-1073c8?labelColor=000000)](https://doi.org/10.5281/zenodo.XXXXXXX)
[![nf-test](https://img.shields.io/badge/unit_tests-nf--test-337ab7.svg)](https://www.nf-test.com)

[![Nextflow](https://img.shields.io/badge/version-%E2%89%A524.04.2-green?style=flat&logo=nextflow&logoColor=white&color=%230DC09D&link=https%3A%2F%2Fnextflow.io)](https://www.nextflow.io/)
[![nf-core template version](https://img.shields.io/badge/nf--core_template-3.3.1-green?style=flat&logo=nfcore&logoColor=white&color=%2324B064&link=https%3A%2F%2Fnf-co.re)](https://github.com/nf-core/tools/releases/tag/3.3.1)
[![run with conda](http://img.shields.io/badge/run%20with-conda-3EB049?labelColor=000000&logo=anaconda)](https://docs.conda.io/en/latest/)
[![run with docker](https://img.shields.io/badge/run%20with-docker-0db7ed?labelColor=000000&logo=docker)](https://www.docker.com/)
[![run with singularity](https://img.shields.io/badge/run%20with-singularity-1d355c.svg?labelColor=000000)](https://sylabs.io/docs/)
[![Launch on Seqera Platform](https://img.shields.io/badge/Launch%20%F0%9F%9A%80-Seqera%20Platform-%234256e7)](https://cloud.seqera.io/launch?pipeline=https://github.com/nf-core/createtaxdb)

[![Get help on Slack](http://img.shields.io/badge/slack-nf--core%20%23createtaxdb-4A154B?labelColor=000000&logo=slack)](https://nfcore.slack.com/channels/createtaxdb)[![Follow on Bluesky](https://img.shields.io/badge/bluesky-%40nf__core-1185fe?labelColor=000000&logo=bluesky)](https://bsky.app/profile/nf-co.re)[![Follow on Mastodon](https://img.shields.io/badge/mastodon-nf__core-6364ff?labelColor=FFFFFF&logo=mastodon)](https://mstdn.science/@nf_core)[![Watch on YouTube](http://img.shields.io/badge/youtube-nf--core-FF0000?labelColor=000000&logo=youtube)](https://www.youtube.com/c/nf-core)

## Introduction

**nf-core/createtaxdb** is a bioinformatics pipeline that constructs custom metagenomic classifier databases for multiple classifiers and profilers from the same input reference genome set in a highly automated and parallelised manner.
It supports both nucleotide and protein based classifiers and profilers.
The pipeline is designed to be a companion pipeline to [nf-core/taxprofiler](https://nf-co.re/taxprofiler/) for taxonomic profiling of metagenomic data, but can be used for any context.

<h1>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/createtaxdb-metromap-diagram-dark.png">
    <img alt="nf-core/createtaxdb" src="assets/createtaxdb-metromap-diagram-light.png">
  </picture>
</h1>

1. Prepares input FASTA files for building
2. Builds databases for:
   - [Bracken](https://doi.org/10.7717/peerj-cs.104)
   - [Centrifuge](https://doi.org/10.1101/gr.210641.116)
   - [DIAMOND](https://doi.org/10.1038/nmeth.3176)
   - [ganon](https://doi.org/10.1093/bioinformatics/btaa458)
   - [Kaiju](https://doi.org/10.1038/ncomms11257)
   - [KMCP](https://doi.org/10.1093/bioinformatics/btac845)
   - [Kraken2](https://doi.org/10.1186/s13059-019-1891-0)
   - [KrakenUniq](https://doi.org/10.1186/s13059-018-1568-0)
   - [MALT](https://doi.org/10.1038/s41559-017-0446-6)

## Usage

> [!NOTE]
> If you are new to Nextflow and nf-core, please refer to [this page](https://nf-co.re/docs/usage/installation) on how to set-up Nextflow. Make sure to [test your setup](https://nf-co.re/docs/usage/introduction#how-to-run-a-pipeline) with `-profile test` before running the workflow on actual data.

First, prepare an input CSV table with your input reference genomes that looks as follows:

```csv
id,taxid,fasta_dna,fasta_aa
Human_Mitochondrial_genome,9606,chrMT.fna,
SARS-CoV-2_genome,694009,GCA_011545545.1_ASM1154554v1_genomic.fna.gz,GCA_011545545.1_ASM1154554v1_genomic.faa.gz
Bacteroides_fragilis_genome,817,GCF_016889925.1_ASM1688992v1_genomic.fna.gz,GCF_016889925.1_ASM1688992v1_genomic.faa.gz
Candidatus_portiera_aleyrodidarum_genome,91844,GCF_000292685.1_ASM29268v1_genomic.fna,GCF_000292685.1_ASM29268v1_genomic.faa
Haemophilus_influenzae_genome,727,GCF_900478275.1_34211_D02_genomic.fna,GCF_900478275.1_34211_D02_genomic.faa
Streptococcus_agalactiae_genome,1311,,GCF_002881355.1_ASM288135v1_genomic.faa
```

Each row contains a human readable name, the taxonomic ID of the organism, and then an (optionally gzipped) Nucleotide and/or Amino Acid FASTA file.

Now, with an appropriate set of taxonomy files you can build databases for multiple profilers - such as Kraken2, ganon, and DIAMOND - in parallel:

```bash
nextflow run nf-core/createtaxdb \
   -profile <docker/singularity/.../institute> \
   --input samplesheet.csv \
   --accession2taxid /<path>/<to>/taxonomy/nucl_gb.accession2taxid \
   --nucl2taxid /<path>/<to>/taxonomy/nucl.accession2taxid.gz \
   --prot2taxid /<path>/<to>/taxonomy/prot.accession2taxid.gz \
   --nodesdmp /<path>/<to>/taxonomy/nodes.dmp \
   --namesdmp /<path>/<to>/taxonomy/names.dmp \
   --build_kraken2 \
   --kraken2_build_options='--kmer-len 45' \
   --build_ganon \
   --ganon_build_options='--kmer-size 45' \
   --build_diamond \
   --diamond_build_options='--no-parse-seqids' \
   --outdir <OUTDIR>
```

The output directory will contain directories containing the database files for each of the profilers you selected to build.
Optionally you can also package these as `tar.gz` archives.

You can also generate pre-prepared input sheets for database specifications of pipelines such as [nf-core/taxprofiler](https://nf-co.re/taxprofiler) using `--generate_downstream_samplesheets`.

> [!WARNING]
> Please provide pipeline parameters via the CLI or Nextflow `-params-file` option. Custom config files including those provided by the `-c` Nextflow option can be used to provide any configuration _**except for parameters**_; see [docs](https://nf-co.re/docs/usage/getting_started/configuration#custom-configuration-files).

For more details and further functionality, please refer to the [usage documentation](https://nf-co.re/createtaxdb/usage) and the [parameter documentation](https://nf-co.re/createtaxdb/parameters).

## Pipeline output

To see the results of an example test run with a full size dataset refer to the [results](https://nf-co.re/createtaxdb/results) tab on the nf-core website pipeline page.
For more details about the output files and reports, please refer to the
[output documentation](https://nf-co.re/createtaxdb/output).

## Credits

nf-core/createtaxdb was originally written by James A. Fellows Yates, Sam Wilkinson, Alexander Ramos Díaz, Lili Andersson-Li and the nf-core community.

We thank the following people for their extensive assistance in the development of this pipeline:

- Zandra Fagernäs for logo design

## Contributions and Support

If you would like to contribute to this pipeline, please see the [contributing guidelines](.github/CONTRIBUTING.md).

For further information or help, don't hesitate to get in touch on the [Slack `#createtaxdb` channel](https://nfcore.slack.com/channels/createtaxdb) (you can join with [this invite](https://nf-co.re/join/slack)).

## Citations

<!-- TODO nf-core: Add citation for pipeline after first release. Uncomment lines below and update Zenodo doi and badge at the top of this file. -->
<!-- If you use nf-core/createtaxdb for your analysis, please cite it using the following doi: [10.5281/zenodo.XXXXXX](https://doi.org/10.5281/zenodo.XXXXXX) -->

An extensive list of references for the tools used by the pipeline can be found in the [`CITATIONS.md`](CITATIONS.md) file.

You can cite the `nf-core` publication as follows:

> **The nf-core framework for community-curated bioinformatics pipelines.**
>
> Philip Ewels, Alexander Peltzer, Sven Fillinger, Harshil Patel, Johannes Alneberg, Andreas Wilm, Maxime Ulysse Garcia, Paolo Di Tommaso & Sven Nahnsen.
>
> _Nat Biotechnol._ 2020 Feb 13. doi: [10.1038/s41587-020-0439-x](https://dx.doi.org/10.1038/s41587-020-0439-x).


<h1>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/images/nf-core-metatdenovo_logo_dark.png">
    <img alt="nf-core/metatdenovo" src="docs/images/nf-core-metatdenovo_logo_light.png">
  </picture>
</h1>

[![GitHub Actions CI Status](https://github.com/nf-core/metatdenovo/actions/workflows/ci.yml/badge.svg)](https://github.com/nf-core/metatdenovo/actions/workflows/ci.yml)
[![GitHub Actions Linting Status](https://github.com/nf-core/metatdenovo/actions/workflows/linting.yml/badge.svg)](https://github.com/nf-core/metatdenovo/actions/workflows/linting.yml)[![AWS CI](https://img.shields.io/badge/CI%20tests-full%20size-FF9900?labelColor=000000&logo=Amazon%20AWS)](https://nf-co.re/metatdenovo/results)[![Cite with Zenodo](http://img.shields.io/badge/DOI-10.5281/zenodo.10666590-1073c8?labelColor=000000)](https://doi.org/10.5281/zenodo.10666590)
[![nf-test](https://img.shields.io/badge/unit_tests-nf--test-337ab7.svg)](https://www.nf-test.com)

[![Nextflow](https://img.shields.io/badge/version-%E2%89%A524.04.2-green?style=flat&logo=nextflow&logoColor=white&color=%230DC09D&link=https%3A%2F%2Fnextflow.io)](https://www.nextflow.io/)
[![nf-core template version](https://img.shields.io/badge/nf--core_template-3.3.1-green?style=flat&logo=nfcore&logoColor=white&color=%2324B064&link=https%3A%2F%2Fnf-co.re)](https://github.com/nf-core/tools/releases/tag/3.3.1)
[![run with conda](http://img.shields.io/badge/run%20with-conda-3EB049?labelColor=000000&logo=anaconda)](https://docs.conda.io/en/latest/)
[![run with docker](https://img.shields.io/badge/run%20with-docker-0db7ed?labelColor=000000&logo=docker)](https://www.docker.com/)
[![run with singularity](https://img.shields.io/badge/run%20with-singularity-1d355c.svg?labelColor=000000)](https://sylabs.io/docs/)
[![Launch on Seqera Platform](https://img.shields.io/badge/Launch%20%F0%9F%9A%80-Seqera%20Platform-%234256e7)](https://cloud.seqera.io/launch?pipeline=https://github.com/nf-core/metatdenovo)

[![Get help on Slack](http://img.shields.io/badge/slack-nf--core%20%23metatdenovo-4A154B?labelColor=000000&logo=slack)](https://nfcore.slack.com/channels/metatdenovo)[![Follow on Bluesky](https://img.shields.io/badge/bluesky-%40nf__core-1185fe?labelColor=000000&logo=bluesky)](https://bsky.app/profile/nf-co.re)[![Follow on Mastodon](https://img.shields.io/badge/mastodon-nf__core-6364ff?labelColor=FFFFFF&logo=mastodon)](https://mstdn.science/@nf_core)[![Watch on YouTube](http://img.shields.io/badge/youtube-nf--core-FF0000?labelColor=000000&logo=youtube)](https://www.youtube.com/c/nf-core)

## Introduction

**nf-core/metatdenovo** is a bioinformatics best-practice analysis pipeline for assembly and annotation of metatranscriptomic and metagenomic data from prokaryotes, eukaryotes or viruses.

On release, automated continuous integration tests run the pipeline on a full-sized dataset on the AWS cloud infrastructure. This ensures that the pipeline runs on AWS, has sensible resource allocation defaults set to run on real-world datasets, and permits the persistent storage of results to benchmark between pipeline releases and other analysis sources. The results obtained from the full-sized test can be viewed on the [nf-core website](https://nf-co.re/metatdenovo/results).

## Usage

![nf-core/metatdenovo metro map](docs/images/metat-metromap.png)

1. Read QC ([`FastQC`](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/))
2. Present QC for raw reads ([`MultiQC`](http://multiqc.info/))
3. Quality trimming and adapter removal for raw reads ([`Trim Galore!`](https://www.bioinformatics.babraham.ac.uk/projects/trim_galore/))
4. Optional: Filter sequences with [`BBduk`](https://jgi.doe.gov/data-and-tools/software-tools/bbtools/bb-tools-user-guide/bbduk-guide/)
5. Optional: Normalize the sequencing depth with [`BBnorm`](https://jgi.doe.gov/data-and-tools/software-tools/bbtools/bb-tools-user-guide/bbnorm-guide/)
6. Merge trimmed, pair-end reads ([`Seqtk`](https://github.com/lh3/seqtk))
7. Choice of de novo assembly programs:
   1. [`RNAspades`](https://cab.spbu.ru/software/rnaspades/) suggested for Eukaryote de novo assembly
   2. [`Megahit`](https://github.com/voutcn/megahit) suggested for Prokaryote de novo assembly
8. Choice of orf caller:
   1. [`TransDecoder`](https://github.com/TransDecoder/TransDecoder) suggested for Eukaryotes
   2. [`Prokka`](https://github.com/tseemann/prokka) suggested for Prokaryotes
   3. [`Prodigal`](https://github.com/hyattpd/Prodigal) suggested for Prokaryotes
9. Quantification of genes identified in assemblies:
   1. Generate index of assembly ([`BBmap index`](https://sourceforge.net/projects/bbmap/))
   2. Mapping cleaned reads to the assembly for quantification ([`BBmap`](https://sourceforge.net/projects/bbmap/))
   3. Get raw counts per each gene present in the assembly ([`Featurecounts`](http://subread.sourceforge.net)) -> TSV table with collected featurecounts output
10. Functional annotation:
    1. [`Eggnog`](https://github.com/eggnogdb/eggnog-mapper) -> Reformat TSV output "eggnog table"
    2. [`KOfamscan`](https://github.com/takaram/kofam_scan)
    3. [`HMMERsearch`](https://www.ebi.ac.uk/Tools/hmmer/search/hmmsearch) -> Ranking orfs based on HMMprofile with [`Hmmrank`](https://github.com/erikrikarddaniel/hmmrank)
11. Taxonomic annotation:
    1. [`EUKulele`](https://github.com/AlexanderLabWHOI/EUKulele) -> Reformat TSV output "Reformat_tax.R"
    2. [`CAT`](https://github.com/dutilh/CAT)
12. Summary statistics table. "Collect_stats.R"

## Usage

> [!NOTE]
> If you are new to Nextflow and nf-core, please refer to [this page](https://nf-co.re/docs/usage/installation) on how to set-up Nextflow. Make sure to [test your setup](https://nf-co.re/docs/usage/introduction#how-to-run-a-pipeline) with `-profile test` before running the workflow on actual data.

First, prepare a samplesheet with your input data that looks as follows:

`samplesheet.csv`:

```
| sample   | fastq_1                   | fastq_2
| -------- | ------------------------- | ------------------------- |
| sample1  | ./data/S1_R1_001.fastq.gz | ./data/S1_R2_001.fastq.gz |
| sample2  | ./data/S2_fw.fastq.gz     | ./data/S2_rv.fastq.gz     |
| sample3  | ./S4x.fastq.gz            | ./S4y.fastq.gz            |
| sample4  | ./a.fastq.gz              | ./b.fastq.gz              |
```

Each row represents a fastq file (single-end) or a pair of fastq files (paired-end).

Now, you can run the pipeline using:

```bash
nextflow run nf-core/metatdenovo \
   -profile <docker/singularity/.../institute> \
   --input samplesheet.csv \
   --outdir <OUTDIR>
```

> [!WARNING]
> Please provide pipeline parameters via the CLI or Nextflow `-params-file` option. Custom config files including those provided by the `-c` Nextflow option can be used to provide any configuration _**except for parameters**_; see [docs](https://nf-co.re/docs/usage/getting_started/configuration#custom-configuration-files).

For more details and further functionality, please refer to the [usage documentation](https://nf-co.re/metatdenovo/usage) and the [parameter documentation](https://nf-co.re/metatdenovo/parameters).

## Pipeline output

To see the results of an example test run with a full size dataset refer to the [results](https://nf-co.re/metatdenovo/results) tab on the nf-core website pipeline page.
For more details about the output files and reports, please refer to the
[output documentation](https://nf-co.re/metatdenovo/output).

> [!NOTE]
> Tables in `summary_tables` directory under the output directory are made especially for further analysis in tools like R or Python.

## Credits

nf-core/metatdenovo was originally written by Danilo Di Leo (@danilodileo), Emelie Nilsson (@emnilsson) & Daniel Lundin (@erikrikarddaniel).

## Contributions and Support

If you would like to contribute to this pipeline, please see the [contributing guidelines](.github/CONTRIBUTING.md).

For further information or help, don't hesitate to get in touch on the [Slack `#metatdenovo` channel](https://nfcore.slack.com/channels/metatdenovo) (you can join with [this invite](https://nf-co.re/join/slack)).

## Citations

If you use nf-core/metatdenovo for your analysis, please cite it using the following doi: [10.5281/zenodo.10666590](https://doi.org/10.5281/zenodo.10666590)

An extensive list of references for the tools used by the pipeline can be found in the [`CITATIONS.md`](CITATIONS.md) file.

You can cite the `nf-core` publication as follows:

> **The nf-core framework for community-curated bioinformatics pipelines.**
>
> Philip Ewels, Alexander Peltzer, Sven Fillinger, Harshil Patel, Johannes Alneberg, Andreas Wilm, Maxime Ulysse Garcia, Paolo Di Tommaso & Sven Nahnsen.
>
> _Nat Biotechnol._ 2020 Feb 13. doi: [10.1038/s41587-020-0439-x](https://dx.doi.org/10.1038/s41587-020-0439-x).