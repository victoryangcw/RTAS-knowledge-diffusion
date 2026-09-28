#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

cp ../figures/Figure1_Roadmap.pdf Fig1.pdf
cp ../figures/Figure2_QuadrantScatter.pdf Fig2.pdf
cp ../figures/Figure3_FundingLevel.pdf Fig3.pdf
cp ../figures/Figure4_DiffusionLag_Stacked.pdf Fig4.pdf
cp ../figures/Figure5_CollegeCaterpillar.pdf Fig5.pdf
cp ../figures/Figure6_HLM_Forest.pdf Fig6.pdf
cp ../figures/Figure7_MatthewEffect.pdf Fig7.pdf

cp ../figures/FigureS1_SupervisorLoad.pdf FigS1.pdf
cp ../figures/FigureS2_QuadrantSummary.pdf FigS2.pdf
cp ../figures/FigureS3a_TopicTrend.pdf FigS3.pdf
cp ../figures/FigureS3b_TopicHeatmap.pdf FigS4.pdf
cp ../figures/FigureS4_CollegeRTAS_Full40.pdf FigS5.pdf

pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex

pdflatex -interaction=nonstopmode -halt-on-error ESM_1.tex
pdflatex -interaction=nonstopmode -halt-on-error ESM_1.tex
