import React, { useEffect } from "react";

import {
  initiateSocket,
  disconnectSocket,
  subscribeToIpcResponse,
  end_job,
  end_run,
} from "./Socket";

import {
  Button,
  Box,
  CssBaseline,
  Typography,
  Grid,
  IconButton,
  Dialog,
  DialogTitle,
} from "@mui/material";

import { red } from "@mui/material/colors";
import { makeStyles } from "@mui/styles";
import { useNavigate } from "react-router-dom";
import logo from "../../assets/images/logo.png";

const useStyles = makeStyles(() => ({
  root: {
    boxShadow:
      "0px 6px 6px -3px rgba(0, 0, 0, 0.2), 0px 10px 14px 1px rgba(0, 0, 0, 0.14), 0px 4px 18px 3px rgba(0, 0, 0, 0.12)",
  },
  logo: {
    height: 60,
  },
  download: {
    height: 18,
    width: 22,
  },
}));

const styles = {
  largeIcon: {
    width: 60,
    height: 60,
  },
};

function Job() {
  const navigate = useNavigate();
  const [open, setOpen] = React.useState(false);
  const [graphOpen, setGraphOpen] = React.useState(false);
  const [isEndRun, setIsEndRun] = React.useState(false);
  const [jobDetails, setJobDetails] = React.useState("");

  let resurveykey = "";
  useEffect(() => {
    initiateSocket((isConnected) => {
      console.log("is socket connected", isConnected);

      subscribeToIpcResponse((err, data) => {
        var response = data.data.replace(/'/g, '"');
        response = response.replace("True", "true");
        response = response.replace("False", "false");
        response = response.replace(/: None/g, ': "None"');

        setJobDetails(JSON.parse(response));
      });
    });
  }, []);

  console.log("job details ", jobDetails);

  if (jobDetails.length !== 0) {
    resurveykey = Object.keys(jobDetails["Operating Parameters"].message)[0];
  }

  const openPopup = () => {
    // setIsSendObj(true);
    setOpen(true);
  };
  const handleClose = () => {
    setOpen(false);
    setIsEndRun(false);
  };

  const handleCancel = () => {
    if (isEndRun) {
      console.log("file tree");

      //emitting end job
      end_job(jobDetails);

      disconnectSocket();
      setIsEndRun(false);

      navigate("/", {
        state: {
          title: "new job",
        },
      });
    } else {
      setOpen(false);
    }
  };

  function handleAccept(e) {
    if (isEndRun) {
      end_run();
      disconnectSocket();
      setIsEndRun(false);

      navigate("/fileUpload", {
        state: {
          title: "new run",
        },
      });
    } else {
      console.log("end job");
      setIsEndRun(true);
    }
  }

  const classes = useStyles();

  return (
    <>
      <Dialog open={open} onClose={handleClose}>
        <Button
          onClick={handleClose}
          sx={{
            justifyContent: "left",
            fontSize: 25,
            width: "10%",
            fontWeight: 1000,
          }}
        >
          X
        </Button>
        <DialogTitle
          sx={{
            fontSize: 30,
            fontWeight: 500,
          }}
        >
          {isEndRun
            ? "Do you want to start another run? "
            : `Are you sure want to end run?`}
          {/* {isEndRun
            ? "Do you want to start another run? "
            : `Are you sure want to end Run ${location.state.jobNumber} ?`} */}
        </DialogTitle>
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
          }}
        >
          <Button
            onClick={handleAccept}
            style={{
              color: "white",
              backgroundColor: red[600],
              marginLeft: 25,
              marginBottom: 30,
              fontSize: 12,
              fontWeight: 500,
              padding: 10,
              marginTop: 30,
            }}
          >
            {isEndRun ? "Yes, Start another run" : "End run"}
          </Button>

          <Button
            onClick={handleCancel}
            autoFocus
            style={{
              marginRight: 25,
              marginBottom: 30,
              fontSize: 12,
              fontWeight: 500,
              padding: 10,
              marginTop: 30,
            }}
          >
            {isEndRun ? "No, end job" : "Cancel"}
          </Button>
        </Box>
      </Dialog>
      <CssBaseline />
      <Box
        sx={{
          display: "flex",
        }}
      >
        <Box
          sx={{
            display: "flex",
            mt: 2,
            marginLeft: 6,
            width: "90%",
            marginRight: 12,
          }}
        >
          <Typography
            variant="h4"
            color="primary"
            sx={{
              fontWeight: "bold",
            }}
            style={{
              fontFamily: "AvertaRegular",
              fontWeight: 700,
              fontSize: 48,
            }}
          >
            Inspection 123456
            {/* {location.state.runNumber} */}
          </Typography>
          <Button
            type="submit"
            //fullWidth
            onClick={openPopup}
            variant="contained"
            sx={{
              marginLeft: 5,
              margintop: "6px",
              textTransform: "initial",
              height: "40px",
            }}
            style={{ fontFamily: "AvertaRegular", fontWeight: 600 }}
          >
            End Inspection
          </Button>
        </Box>
        <IconButton>
          <img className={classes.logo} src={logo} alt="Logo" />
        </IconButton>
      </Box>
      <Box
        sx={{
          display: "flex",
          marginLeft: 6,
          marginRight: 4,
        }}
      >
        <Typography
          variant="h6"
          color="secondary"
          sx={{
            marginRight: 1,
            flex: 1,
          }}
          style={{ fontFamily: "AvertaRegular", fontSize: 24 }}
        >
          {/* JOB {location.state.jobNumber} */}
          Job 123456
        </Typography>
      </Box>
      <Box
        sx={{
          display: "flex",
          marginLeft: 6,
          marginRight: 6,
          mt: 4,
        }}
      >
        <Typography
          variant="body1"
          color="secondary"
          sx={{ textTransform: "uppercase" }}
          style={{ fontFamily: "AvertaBold", fontSize: 18 }}
        >
          operating parameters
        </Typography>
      </Box>
      <Box sx={{ display: "flex", marginLeft: 6, marginRight: 6 }}>
        <Box
          sx={{
            display: "flex",
            flexDirection: "column",
            minWidth: "30%",
          }}
        >
          <Box
            sx={{
              height: "60%",
              padding: "5px",
              boxShadow:
                "0px 3px 5px -1px rgba(0, 0, 0, 0.2), 0px 5px 8px rgba(0, 0, 0, 0.14), 0px 1px 14px rgba(0, 0, 0, 0.12)",
              borderBottom: 10,
              marginRight: 3,
              marginBottom: 1,
              borderRadius: 2,
              borderBottomColor:
                resurveykey === "Job continues" ? "#67ac5b" : "#EB0029",
              marginTop: 1,
            }}
          >
            <Typography
              //gutterBottom
              variant="h4"
              color={resurveykey === "Job continues" ? "#67ac5b" : "#EB0029"}
              align="center"
              sx={{
                marginTop: 2,
              }}
              style={{ fontFamily: "AvertaBold", fontSize: 36 }}
            >
              {Object.keys(jobDetails).length > 0
                ? `${jobDetails["Operating Parameters"].quality_control}`
                : ""}
            </Typography>
            <Typography
              variant="body2"
              color="#8A8C8C"
              align="center"
              sx={{
                marginBottom: 2,
              }}
              style={{
                fontFamily: "AvertaRegular",
                fontSize: 14,
                fontWeight: 600,
              }}
            >
              QUALITY CONTROL
            </Typography>
          </Box>
          <Box
            sx={{
              height: "40%",
              padding: "5px",
              boxShadow:
                "0px 3px 5px -1px rgba(0, 0, 0, 0.2), 0px 5px 8px rgba(0, 0, 0, 0.14), 0px 1px 14px rgba(0, 0, 0, 0.12)",
              marginRight: 3,
              marginBottom: 1,
              borderRadius: 2,
              //borderWidth: 100,
              marginTop: 2,
            }}
          >
            <Typography
              //gutterBottom
              variant="h4"
              color="secondary"
              align="center"
              sx={{
                marginTop: 2,
              }}
              style={{ fontFamily: "AvertaBold", fontSize: 36 }}
            >
              {Object.keys(jobDetails).length > 0
                ? `${jobDetails["Operating Parameters"].tool_status}`
                : ""}
            </Typography>
            <Typography
              gutterBottom
              variant="body2"
              color="#8A8C8C"
              align="center"
              sx={{
                fontWeight: "bold",
                marginBottom: 4,
                textTransform: "uppercase",
              }}
              style={{
                fontFamily: "AvertaRegular",
                fontSize: 14,
                fontWeight: 600,
              }}
            >
              Wind turbine status
            </Typography>
          </Box>
        </Box>
        <Box
          sx={{
            display: "flex",
            flexDirection: "column",
            minWidth: "70%",
          }}
        >
          <Box
            sx={{
              height: "100%",
              padding: "5px",
              boxShadow:
                "0px 3px 5px -1px rgba(0, 0, 0, 0.2), 0px 5px 8px rgba(0, 0, 0, 0.14), 0px 1px 14px rgba(0, 0, 0, 0.12)",
              borderBottom: 10,
              //marginRight: 2,
              marginBottom: 1,
              borderRadius: 2,
              borderBottomColor:
                resurveykey === "Job continues" ? "#67ac5b" : "#EB0029",
              marginTop: 1,
              flexDirection: "row",
            }}
          >
            <Box sx={{ display: "flex", alignItems: "center", height: "100%" }}>
              <Box
                sx={{
                  // display: "flex",
                  // flexDirection: "column",
                  minWidth: "40%",
                }}
              >
                <Typography
                  variant="h3"
                  color={
                    resurveykey === "Job continues" ? "#67ac5b" : "#EB0029"
                  }
                  align="center"
                  style={{ fontFamily: "AvertaBold", fontSize: 48 }}
                >
                  {resurveykey}
                </Typography>
              </Box>
              <Box
                sx={{
                  // display: "flex",
                  // flexDirection: "column",
                  minWidth: "60%",
                }}
              >
                <Typography
                  variant="body2"
                  color="secondary"
                  align="left"
                  sx={{
                    textTransform: "uppercase",
                  }}
                  style={{
                    fontFamily: "AvertaRegular",
                    fontSize: 14,
                    fontWeight: 600,
                  }}
                >
                  Component Status
                </Typography>
                <Typography
                  variant="body1"
                  color="secondary"
                  align="left"
                  sx={{
                    //fontWeight: 'bold',
                    marginLeft: 1,
                    //textTransform: "uppercase"
                  }}
                  style={{
                    fontFamily: "AvertaRegular",
                    fontSize: 14,
                  }}
                >
                  •{" "}
                  {Object.keys(jobDetails).length > 0 &&
                    jobDetails["Operating Parameters"].message[resurveykey][
                      "Site Environment"
                    ]}
                </Typography>
                <Typography
                  variant="body2"
                  color="secondary"
                  align="left"
                  sx={{
                    textTransform: "uppercase",
                    marginTop: 6,
                  }}
                  style={{
                    fontFamily: "AvertaRegular",
                    fontSize: 14,
                    fontWeight: 600,
                  }}
                >
                  recommended action
                </Typography>
                <Typography
                  variant="body1"
                  color="secondary"
                  align="left"
                  sx={{
                    //fontWeight: 'bold',
                    marginLeft: 1,
                    //textTransform: "uppercase"
                  }}
                  style={{
                    fontFamily: "AvertaRegular",
                    fontSize: 14,
                  }}
                >
                  •{" "}
                  {Object.keys(jobDetails).length > 0 &&
                    jobDetails["Operating Parameters"].message[resurveykey][
                      "Recommended Action"
                    ]}
                </Typography>
              </Box>
            </Box>
          </Box>
        </Box>
      </Box>
      <Box
        sx={{
          display: "flex",
          marginLeft: 6,
          marginRight: 6,
          mt: 4,
        }}
      >
        <Typography
          variant="body1"
          color="secondary"
          sx={{ textTransform: "uppercase" }}
          style={{ fontFamily: "AvertaBold", fontSize: 18 }}
        >
          sensor data
        </Typography>
      </Box>
      <Box sx={{ width: "70%", marginLeft: 6, marginRight: 6 }}>
        <Grid container rowSpacing={1} columnSpacing={{ xs: 1, sm: 2, md: 3 }}>
          <Grid item xs={6}>
            <Grid
              container
              rowSpacing={1}
              columnSpacing={{ xs: 1, sm: 2, md: 3 }}
            >
              <Grid item xs={6}>
                <Box
                  sx={{
                    padding: "5px",
                    boxShadow:
                      "0px 3px 5px -1px rgba(0, 0, 0, 0.2), 0px 5px 8px rgba(0, 0, 0, 0.14), 0px 1px 14px rgba(0, 0, 0, 0.12)",
                    borderRadius: 2,
                    marginTop: 1,
                  }}
                >
                  <Typography
                    //gutterBottom
                    variant="h4"
                    color="secondary"
                    align="center"
                    sx={{
                      marginTop: 2,
                    }}
                    style={{
                      fontFamily: "AvertaRegular",
                      fontWeight: 700,
                      fontSize: 24,
                    }}
                  >
                    {Object.keys(jobDetails).length > 0
                      ? `${jobDetails["Sensor Data"].power_curve}`
                      : ""}
                  </Typography>
                  <Typography
                    gutterBottom
                    variant="body2"
                    color="#8A8C8C"
                    align="center"
                    sx={{
                      fontWeight: "bold",
                      marginBottom: 4,
                      textTransform: "uppercase",
                    }}
                    style={{
                      fontFamily: "AvertaRegular",
                      fontWeight: 600,
                      fontSize: 14,
                    }}
                  >
                    Power Curve (kWh)
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6}>
                <Box
                  sx={{
                    padding: "5px",
                    boxShadow:
                      "0px 3px 5px -1px rgba(0, 0, 0, 0.2), 0px 5px 8px rgba(0, 0, 0, 0.14), 0px 1px 14px rgba(0, 0, 0, 0.12)",
                    borderRadius: 2,
                    marginTop: 1,
                  }}
                >
                  <Typography
                    //gutterBottom
                    variant="h4"
                    color="secondary"
                    align="center"
                    sx={{
                      marginTop: 2,
                    }}
                    style={{
                      fontFamily: "AvertaRegular",
                      fontWeight: 700,
                      fontSize: 24,
                    }}
                  >
                    {Object.keys(jobDetails).length > 0
                      ? `${jobDetails["Sensor Data"].lv_activepower}`
                      : ""}
                  </Typography>
                  <Typography
                    gutterBottom
                    variant="body2"
                    color="#8A8C8C"
                    align="center"
                    sx={{
                      marginBottom: 4,
                      textTransform: "uppercase",
                    }}
                    style={{
                      fontFamily: "AvertaRegular",
                      fontWeight: 600,
                      fontSize: 14,
                    }}
                  >
                    LV Active Power (kW)
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </Grid>
          <Grid item xs={6}>
            <Grid
              container
              rowSpacing={1}
              columnSpacing={{ xs: 1, sm: 2, md: 3 }}
            >
              <Grid item xs={6}>
                <Box
                  sx={{
                    padding: "5px",
                    boxShadow:
                      "0px 3px 5px -1px rgba(0, 0, 0, 0.2), 0px 5px 8px rgba(0, 0, 0, 0.14), 0px 1px 14px rgba(0, 0, 0, 0.12)",
                    borderRadius: 2,
                    marginTop: 1,
                  }}
                >
                  <Typography
                    //gutterBottom
                    variant="h4"
                    color="secondary"
                    align="center"
                    sx={{
                      marginTop: 2,
                    }}
                    style={{
                      fontFamily: "AvertaRegular",
                      fontWeight: 700,
                      fontSize: 24,
                    }}
                  >
                    {Object.keys(jobDetails).length > 0
                      ? `${jobDetails["Sensor Data"].wind_speed}`
                      : ""}
                  </Typography>
                  <Typography
                    gutterBottom
                    variant="body2"
                    color="#8A8C8C"
                    align="center"
                    sx={{
                      marginBottom: 4,
                      textTransform: "uppercase",
                    }}
                    style={{
                      fontFamily: "AvertaRegular",
                      fontWeight: 600,
                      fontSize: 14,
                    }}
                  >
                    Wind Speed (mph)
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6}>
                <Box
                  sx={{
                    padding: "5px",
                    boxShadow:
                      "0px 3px 5px -1px rgba(0, 0, 0, 0.2), 0px 5px 8px rgba(0, 0, 0, 0.14), 0px 1px 14px rgba(0, 0, 0, 0.12)",
                    borderRadius: 2,
                    marginTop: 1,
                  }}
                >
                  <Typography
                    //gutterBottom
                    variant="h4"
                    color="secondary"
                    align="center"
                    sx={{
                      marginTop: 2,
                    }}
                    style={{
                      fontFamily: "AvertaRegular",
                      fontWeight: 700,
                      fontSize: 24,
                    }}
                  >
                    {Object.keys(jobDetails).length > 0
                      ? `${jobDetails["Sensor Data"].wind_direction}º`
                      : ""}
                  </Typography>
                  <Typography
                    gutterBottom
                    variant="body2"
                    color="#8A8C8C"
                    align="center"
                    sx={{
                      marginBottom: 4,
                      textTransform: "uppercase",
                    }}
                    style={{
                      fontFamily: "AvertaRegular",
                      fontWeight: 600,
                      fontSize: 14,
                    }}
                  >
                    Wind Direction
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </Grid>
        </Grid>
      </Box>
      <Box
        sx={{
          display: "flex",
          marginLeft: 2,
          mt: 8,
        }}
      >
        <Typography
          variant="body1"
          color="secondary"
          sx={{ textTransform: "uppercase" }}
          style={{
            fontFamily: "AvertaRegular",
            fontWeight: 700,
            fontSize: 16,
          }}
        >
          {" Application version: "}
        </Typography>
        <Typography
          variant="body1"
          color="secondary"
          sx={{ textTransform: "uppercase", height: "24px" }}
          style={{
            fontFamily: "AvertaRegular",
            fontSize: 16,
          }}
        >
          v1.0.1
        </Typography>
      </Box>
    </>
  );
}

export default Job;
