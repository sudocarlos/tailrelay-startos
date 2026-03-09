FROM sudocarlos/tailrelay:v0.7.0

# Copy the StartOS entrypoint wrapper
COPY docker_entrypoint.sh /usr/local/bin/docker_entrypoint.sh
RUN chmod +x /usr/local/bin/docker_entrypoint.sh

# Copy known StartOS service targets
COPY assets/startos_targets.json /targets.json
