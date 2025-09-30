# HowTo deploy on CG2
How  to deploy workload on CG2 with all possible configurations and advices.

## Configuration

### Image build
#### Build docker image onboard
If there is a need to customize one of the docker base images,do a Dockerfile that has one of our proposed base images pre-loaded as a first `FROM` keyword.
This Dockerfile will ideally only copy the binary/script needed onto the docker image and will be built on the satellite.
More info to build an image [here](./howto-docker).

#### Embed a custom made docker image
Please cotact us ASAP for a chance to onboard a docker container before launch as the data throuput is limited in-orbit.

### Filesystem
In the docker container there will be a data folder that will be mounted.
The mount location is by default `/data` but can be configured by the user.
Example after deployment of the customer from inside his container (default config) : 
```
/data
    Dockerfile
    my_build_files/
    my_first_upload.txt
    put_here_the_files_you want_to_transmit_to_ground 
```

So for the downlink back to earth, client apps should put files under the /data directory. This will be the only path checked for downloadable artifacts. It will be managed by the client dashboard afterwards via a git-like approach.

To uplink artifacts, it would be from the ground dashboard, and files will go into the /data directory directly.
Note that as said previously /data is the default configuration, one can change it at the first onboarding transfer.

### Scheduling
There are multiple ways to schedule a worload in CG2.
However if this is not wanted, and simply run whenever possible, avoir having a configuration for scheduling.

#### Time based
To execute at a certain point in time, simply have a RFC2339 time reference as the following : 2025-05-22T12:10:00+02:00

#### Location based
To execute hover a certain location, the configuration of the latitude and longitude is needed.
For this one can use this as an example :

```
latitude: 46.27
longitude: 6.96
altitude: 372.0
min_elevation: 5.0
```

Note that this feature is still testing, and a lot can still change.
For now it's more on a best-effort basis and min elevation is not guaranteed.

### Telemetry access
Onboard telementry data could be accessed for those who are interested.
There will be a REST API available if you request telemetry data from the satellite.
More info on the API and how to use it : [CG2 Telemetry](./onboard-telemetry)
### Specific computing needs
*TBD how to implement this*

#### FPGA
To use the onboard PL of the FPGA, please contact us ASAP, we might need kernel modules from you, and asses the feasability.

#### GPU
To use the GPU, ask also in the configuration to have access to it, it will be loaded then by docker using the equivalent of --gpus command.
The onboard GPU is a jetson board, and some AI base images are already pre-loaded in the satellite to use it, please have a look !

## Deployment
### Asking DPhi operators
One simple way to deploy workload is to send to DPhi operators a set of configuration as explained above.
In short: 
- A build directory with DOckerfile and necessary files to build (remember to optimize for size)
- A set of configuration wanted (scheduling, other mount point)

### Uplink / Downlink
From the dashboard you must be able to ask for uplink/downlink files to the data directory as explained above.
