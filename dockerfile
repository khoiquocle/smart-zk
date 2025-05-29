FROM apwbs/martsia:martsia_ethereum

# Add user kevin (optional)
RUN echo "kevin:x:1000:1000::/home/kevin:/bin/bash" >> /etc/passwd && \
    echo "kevin:x:1000:" >> /etc/group

# Install dependencies: curl, git, build tools, etc.
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    pkg-config \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Rust (via rustup) and set PATH permanently
RUN curl https://sh.rustup.rs -sSf | bash -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Install Node.js 16.x (LTS)
RUN curl -sL https://deb.nodesource.com/setup_16.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Install snarkjs globally
RUN npm install -g snarkjs 

# Set up a working directory for circomlib install
WORKDIR /zkbuild
RUN npm init -y && npm install circomlib

# Optionally copy circomlib to /test if your Circom files expect it there
RUN mkdir -p /test && cp -r node_modules /test/

# Clone and build circom from source
RUN git clone https://github.com/iden3/circom.git /circom && \
    cd /circom/circom && \
    cargo build --release && \
    cargo install --path .

# Remove old IPFS if it exists and install latest IPFS (Kubo)
RUN which ipfs && rm -f $(which ipfs) || true && \
    IPFS_VERSION="v0.26.0" && \
    ARCH="linux-amd64" && \
    cd /tmp && \
    wget "https://dist.ipfs.tech/kubo/${IPFS_VERSION}/kubo_${IPFS_VERSION}_${ARCH}.tar.gz" && \
    tar -xzf "kubo_${IPFS_VERSION}_${ARCH}.tar.gz" && \
    cd kubo && \
    ls -la && \
    chmod +x ipfs && \
    cp ipfs /usr/local/bin/ && \
    chmod +x /usr/local/bin/ipfs && \
    cd /tmp && \
    rm -rf kubo "kubo_${IPFS_VERSION}_${ARCH}.tar.gz"

# Verify IPFS installation and initialize (remove old repo first)
RUN rm -rf ~/.ipfs && \
    /usr/local/bin/ipfs --version && \
    /usr/local/bin/ipfs init

# Update PATH to ensure new IPFS is found first
ENV PATH="/usr/local/bin:${PATH}"

# Install benchmark dependencies
RUN pip3 install --no-cache-dir \
    psutil>=5.8.0 \
    matplotlib>=3.5.0 \
    seaborn>=0.11.0 \
    plotly>=5.0.0 \
    pandas>=1.3.0 \
    numpy>=1.21.0 \
    tqdm>=4.62.0 \
    tabulate>=0.8.9

# Create benchmark results directory
RUN mkdir -p /test/benchmark_results /test/benchmark_charts

# Final working directory
WORKDIR /test

CMD ["/bin/bash"]
