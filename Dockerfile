# Same image runs locally (Phase 1) and on a cloud box / CI runner (Phase 2).
#   docker build -t mathshorts .
#   docker run --rm -v "$PWD":/app mathshorts ms status
#   docker run --rm -v "$PWD":/app mathshorts ms preview 0001
FROM python:3.13-slim

ENV DEBIAN_FRONTEND=noninteractive PYTHONDONTWRITEBYTECODE=1 PIP_NO_CACHE_DIR=1

# ffmpeg: encode/mix. Cairo/Pango: Manim's text and vector rendering.
# A trimmed TeX Live + dvisvgm: MathTex labels (sqrt5, theta). fonts-inter: the channel font.
RUN apt-get update && apt-get install -y --no-install-recommends \
        ffmpeg build-essential pkg-config libcairo2-dev libpango1.0-dev \
        texlive-latex-base texlive-latex-extra texlive-fonts-recommended texlive-science \
        dvisvgm fonts-inter git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml ./
COPY pipeline ./pipeline
COPY lib ./lib
RUN pip install -e .

# The repo is bind-mounted over /app at run time, so edits on the host are live.
CMD ["ms", "status"]
