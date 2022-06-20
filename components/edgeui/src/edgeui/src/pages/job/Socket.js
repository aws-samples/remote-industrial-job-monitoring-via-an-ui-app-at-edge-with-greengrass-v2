import io from "socket.io-client";
// import ipAddress from "../../IpAddress";

let socket;

//Emitter
export const initiateSocket = async (isConnected) => {
  let ip = localStorage.getItem("IpAddress");
  socket = io.connect(`http://${ip}:8080/`);
  console.log(`Connecting socket from ip address ${ip}`);

  socket.on("connect", function () {
    console.log("publish_msg emitted");
    socket.emit("publish_msg", { data: "" });
    return isConnected(socket.connected);
  });
  // socket.emit("my_event", { data: "I'm connected!" });
  // socket.emit("publish_msg", { data: "" });
};

//End Job
export const end_job = (payload) => {
  console.log("End job emitter", payload);
  socket.emit("end_job", payload);
};

//End Run
export const end_run = () => {
  console.log("End run emitter");
  socket.emit("end_run");
};

//Disconnect
export const disconnectSocket = () => {
  console.log("Disconnecting socket...");
  socket.emit("disconnect_request");
  socket.on("disconnect", function () {
    console.log("is connected", socket.connected);
  });
};

//Subscriber
export const subscribeToIpcResponse = (cb) => {
  console.log("subscribing to IPC response");

  socket.on("ipc_response", (msg) => {
    console.log("IPC response received");

    return cb(null, msg);
  });
};

// export const subscribeToMyResponse = (cb) => {
//   socket.on("my_response", (msg) => {
//     console.log("Websocket event received!");
//     return cb(null, msg);
//   });
// };

// //Emitters
// export const myEvent = (room, message) => {
//   if (socket) socket.emit("my_event", { message, room });
// };
// export const publishMessage = (room, message) => {
//   if (socket) socket.emit("publish_msg", { message, room });
// };
// export const disconnectRequest = (room, message) => {
//   if (socket) socket.emit("disconnect_request", { message, room });
// };
