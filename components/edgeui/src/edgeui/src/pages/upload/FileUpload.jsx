import React, { useState, useEffect, useRef } from "react";
import {
  Button,
  Box,
  Container,
  CssBaseline,
  Typography,
  Alert,
  CircularProgress,
} from "@mui/material";
import { makeStyles } from "@mui/styles";
import { useNavigate, useLocation } from "react-router-dom";
import upload from "../../assets/icons/upload.png";
import json from "../../assets/icons/json.png";
import logo from "../../assets/images/logo.png";

const useStyles = makeStyles((theme) => ({
  root: {
    borderRadius: 4,
    boxShadow:
      "0px 6px 6px -3px rgba(0, 0, 0, 0.2), 0px 10px 14px 1px rgba(0, 0, 0, 0.14), 0px 4px 18px 3px rgba(0, 0, 0, 0.12)",
  },
  logo: {
    height: theme.spacing(18),
  },
  dropCSV: {
    width: "500px",
    height: "250px",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    margin: "2rem auto",
    border: "1px dashed #8A8C8C",
    borderRadius: 4,
  },
  upload: {
    height: 40,
    width: 40,
    alignSelf: "center",
    marginBottom: 15,
  },
}));

function removeItems(arr, item) {
  for (var i = 0; i < item; i++) {
    arr.pop();
  }
}

function useFiles({ initialState = [], maxFiles }) {
  const [state, setstate] = useState(initialState);
  function withBlobs(files) {
    const destructured = [...files];
    if (destructured.length > maxFiles) {
      const difference = destructured.length - maxFiles;
      removeItems(destructured, difference);
    }
    const blobs = destructured
      .map((file) => {
        return file;
      })
      .filter((elem) => elem !== null);

    setstate(blobs);
  }
  return [state, withBlobs];
}

function FileUpload({ onDrop, maxFiles = 1 }) {
  const location = useLocation();
  const classes = useStyles();
  let navigate = useNavigate();
  const [disable, setDisable] = useState(true);
  const [files, setfiles] = useFiles({ maxFiles });
  const [fileName, setFileName] = useState("");
  const [error, setError] = React.useState("");
  const [showSpinner, setShowSpinner] = useState(false);

  const $input = useRef(null);
  useEffect(() => {
    if (onDrop) {
      onDrop(files);
    }
  }, [files]);

  useEffect(() => {
    setTimeout(() => {
      setError("");
    }, 4000);
  }, [error]);

  const handleSubmission = async () => {
    console.log("handleSubmission");
    setShowSpinner(true);
    if (typeof files[0] != "undefined") {
      console.log("selectedFile", files);
      const formData = new FormData();
      formData.append("filename", files[0]);
      let ip = localStorage.getItem("IpAddress");
      fetch(`http://${ip}:8081/uploadfile`, {
        method: "POST",
        body: formData,
      })
        .then((response) => response.json())
        .then((result) => {
          console.log("Success:", result);
          setShowSpinner(false);
          navigate("/job");
        })
        .catch((error) => {
          setShowSpinner(false);
          console.error("Error:", error);
        });
    } else {
      console.log("undefined");
    }
  };

  return (
    <Container component="main" maxWidth="sm">
      <CssBaseline />

      <Box
        sx={{
          marginTop: 8,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          marginBottom: 5,
        }}
      >
        <img className={classes.logo} src={logo} alt="Logo" />

        <Box
          // sx={{
          //   marginTop: 1,
          // }}
          //component="form"
          //onSubmit={handleSubmit}
          noValidate
          className={classes.root}
        >
          {error && <Alert severity="error">{error}</Alert>}
          <Box p={5}>
            <Typography
              component="h1"
              variant="h4"
              color="primary"
              align="left"
              fontWeight="700"
              fontFamily="AvertaRegular"
            >
              <Box sx={{ fontWeight: "bold", m: 1 }}>
                Start a new inspection
                {/* {location?.state?.title ? location?.state?.title : "new job"} */}
              </Box>
            </Typography>
            <Box
              onClick={() => {
                $input.current.click();
                console.log("onClick file open");
              }}
              onDrop={(e) => {
                console.log("onDrop");
                e.preventDefault();
                e.persist();
                // setfiles(e.dataTransfer.files);
                // setover(false);
              }}
              onDragOver={(e) => {
                console.log("onDragOver");
                e.preventDefault();
                // setfiles(e.dataTransfer.files);
                // setover(true);
              }}
              onDragLeave={(e) => {
                console.log("onDragLeave");
                e.preventDefault();
                // setfiles(e.dataTransfer.files);
                // setover(false);
              }}
              className={classes.dropCSV} //{over ? "upload-container over" : "upload-container"}
            >
              <Box
                sx={{
                  display: "flex",
                  flexDirection: "column",
                  //minWidth: "30%",
                }}
              >
                <img
                  className={classes.upload}
                  src={fileName.length === 0 ? upload : json}
                  alt="Logo"
                />
                <Typography
                  variant="h7"
                  color="#8A8C8C"
                  align="center"
                  fontFamily="AvertaRegular"
                >
                  {fileName.length === 0
                    ? "Upload run configuration file"
                    : fileName}
                </Typography>
                <Typography
                  variant="h7"
                  color="#B1AEAE"
                  align="center"
                  fontFamily="AvertaRegular"
                >
                  {fileName.length === 0 ? "(Contact support to get file)" : ""}
                </Typography>
                <br />
                <Typography
                  variant="h7"
                  color="#B1AEAE"
                  align="center"
                  fontFamily="AvertaRegular"
                >
                  {fileName.length === 0 ? "JSON FILES SUPPORTED" : ""}
                </Typography>
              </Box>
              <input
                style={{ display: "none" }}
                type="file"
                name="file"
                //accept="image/*"
                ref={$input}
                onChange={(e) => {
                  console.log("file length", e.target.files.length);
                  if (e.target.files.length === 0) {
                    return;
                  }

                  if (e.target.files[0].name.split(".").pop() === "json") {
                    console.log("file uploaded");
                    setDisable(false);
                    console.log(e.target.files[0].name);
                    setfiles(e.target.files);
                    setFileName(e.target.files[0].name);
                  } else {
                    setError("Please upload json file");
                    console.log("invalid file uploaded");
                  }
                }}
                multiple={maxFiles > 1}
              />
            </Box>
            <Button
              disabled={disable}
              type="submit"
              variant="contained"
              sx={{ mt: 3, mb: 2, textTransform: "initial" }}
              onClick={handleSubmission}
              style={{ fontFamily: "AvertaRegular", fontWeight: 600 }}
            >
              {showSpinner === true && (
                <CircularProgress
                  size={30}
                  sx={{
                    color: "#4b9dff",
                    position: "absolute",
                  }}
                />
              )}

              {location?.state?.title === "new run"
                ? "Start run"
                : "Start inspection"}
            </Button>
          </Box>
        </Box>
      </Box>
    </Container>
  );
}

export default FileUpload;
