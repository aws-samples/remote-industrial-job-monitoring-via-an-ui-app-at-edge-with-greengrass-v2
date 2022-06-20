## Real-Time IoT Data Process and Monitor via an UI Application @Edge with AWS IoT Greengrass

making for efficiency and safety reasons. To reduce the unexpected network interruption and delay of IoT data analysis, Edge Computing becomes a desirable option for real-time IoT data processing and monitoring. Edge Computing is a system of micro computing/storage devices that are installed at the edge of the network, allowing efficient processing of data locally. For Industrial sites, such as remote power plants, oil rig and factory floor, edge application with UI component offers great advantage for uninterrupted monitoring and control, and enabled autonomous operation for plant/rig workers.  

This repository will showcase an Edge UI application with AWS IoT Greengrass v2. This Edge UI application contains multiple custom GGv2 components to achieve flexible data ingestion, and streaming data analytics and visualization at the Edge. The application deployment, updates across multiple edge devices can be easily achieved via GGv2 runtime. 

### Use case 1: 

Operators on factory floor may have some reports or IoT job metadata that cannot be ingested via a pre-defined IoT data model automatically to the cloud. This UI provides a “FileUpload” page, that uses a frontend ggv2 component to ingest a JSON file, and send the file data to a backend component. Then the backend component will send the data to a GGv2 pre-built component: Stream manager. This Stream manager component will achieve two goals: (1) local data storage; (2) transfers data from local edge device to the AWS Cloud. As a pre-built component, it offers flexible target destination in the cloud, including S3, Kinesis, AWS IoT SiteWise and IoT Analytics. It is designed to work in environments with intermittent or limited connectivity. Users can define multiple data exportation configurations when the edge device is connected or disconnected. User can also set priorities to control the order in which the AWS IoT Greengrass Core exports streams to the AWS Cloud, so that the critical data can be exported first when internet connection resumed.  

In this use case, the unmapped data will land in S3. A variety of data analytic tools (Amazon Glue and Athena) /BI tools can be used in AWS Cloud to analysis this metadata with other IoT time series data in a flexible manner. 

### Use case 2: 

Operator needs to make judgements with streaming IoT data in a near real time fashion, and it will facilitate operator to make right decisions if IoT data can be shown in an interactive UI application with low latency. With this App, operator can make sound decisions on site without delay and improve plant operation efficiently. In this edge UI application, there is a “dummy publisher” component that simulates outputs from a wind turbine facility. The publish frequency from this dummy publisher is once per 10 seconds. A websocket component is subscribing to streaming data from the dummy publisher via Inter-process communication (IPC) with AWS IoT GGv2, and send the data to the edge UI app via websocket communication. Please note, this “dummy publisher” component is used for demonstration purpose only. In the industrial plant setting, it will be replaced by a suitable industrial data connector to wind turbines (e.g. SCADA system).

### Solution Overview

Here is the solution architecture of this workflow at the Edge. Four user defined components: (1) A frontend UI component written in ReactJS, which contains all UI pages used in both use cases; (2) A “JSON FileUploader” component written in Python, that can collect file data from the frontend UI, and send the JSON information to S3 via Stream Manager. (3) a “Dummy Publisher” publishes wind turbine data at a rate of one message per 10 seconds, and sends the message to a websocket component via IPC protocol. (4) Finally, a websocket component serves the streaming messages from “Publisher” to UI component via a websocket server. 

* Link to architecture diagram(s)
![EdgeUI Architecture](ArchDiagram.jpg?raw=true "Edge UI Architecture")

Besides these custom GGv2 components, there are two pre-built GGv2 components are deployed with this solution: (1) log manager for application monitoring and (2) stream manager for edge device data exportation.  

In this repository, an Ubuntu 22.04 LTS EC2 instance with AWS IoT GreenGrass v2 runtime was used to simulate an edge device with AWS IoT platform. 

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

