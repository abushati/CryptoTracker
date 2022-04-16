import React, { useEffect, useRef, useState } from "react";
import ReactDOM from "react-dom";
import styled from "styled-components";
import MenuItem from '@mui/material/MenuItem';
import Select, { SelectChangeEvent } from '@mui/material/Select';
import InputLabel from '@mui/material/InputLabel';
import FormControl from '@mui/material/FormControl';
import OutlinedInput from '@mui/material/OutlinedInput';
import InputAdornment from '@mui/material/InputAdornment';
import Radio from '@mui/material/Radio';
import RadioGroup from '@mui/material/RadioGroup';
import FormLabel from '@mui/material/FormLabel';
import FormControlLabel from '@mui/material/FormControlLabel';
import Button from '@mui/material/Button';
import Snackbar from '@mui/material/Snackbar';
import MuiAlert from '@mui/material/Alert';
//https://devrecipes.net/modal-component-with-next-js/
// let setNewAlertData = {}
const Modal = ({ show, onClose, coinInfo }) => {
    const [isBrowser, setIsBrowser] = useState(false);
    const [alertType, setAlertType] = useState("");   
    const [formFields, setFormFields] = useState ([])
    const [newAlertData, setNewAlertData] = useState({})
    const [enableSaveButton, setEnableSaveButton] = useState(false)
    const [successSave, setSuccessSave] = useState(false)

    const Alert = React.forwardRef(function Alert(props, ref) {
      return <MuiAlert elevation={6} ref={ref} variant="filled" {...props} />;
    });

    useEffect(() => {
      setIsBrowser(true);
    }, []);
  
    const handleCloseClick = (e) => {
      e.preventDefault();
      setNewAlertData({})
      setFormFields([])
      setAlertType("")
      setEnableSaveButton(false)
      setSuccessSave(false)
      onClose();

    };

  const rebuildForm = (alertType) => {
      let type = alertType
      let additionalFormFields = {'price': 
                                      <div>
                                        <InputLabel htmlFor="outlined-adornment-amount">Amount</InputLabel>
                                          <OutlinedInput
                                              id="outlined-adornment-amount"
                                              value={newAlertData['threshold']}
                                              onChange={(e) => addDataToAlert('threshold',e.target.value)}
                                              startAdornment={<InputAdornment position="start">$</InputAdornment>}
                                              label="Amount"
                                            />
                                        <FormLabel id="demo-radio-buttons-group-label">Condition</FormLabel>
                                          <RadioGroup
                                              aria-labelledby="demo-controlled-radio-buttons-group"
                                              name="controlled-radio-buttons-group"
                                              value={newAlertData['threshold_condition']}
                                              onChange={(e) => addDataToAlert('threshold_condition',e.target.value)}
                                            >
                                              <FormControlLabel value="above" control={<Radio />} label="Above Price" />
                                              <FormControlLabel value="below" control={<Radio />} label="Below Price" />
                                            </RadioGroup>
                                      </div> ,
                                'percent':
                                    <div>
                                      <InputLabel htmlFor="outlined-adornment-amount">Percent Change</InputLabel>
                                        <OutlinedInput
                                            id="outlined-adornment-amount"
                                            value={newAlertData['threshold']}
                                            onChange={(e) => addDataToAlert('threshold',e.target.value)}
                                            startAdornment={<InputAdornment position="start">%</InputAdornment>}
                                            label="Amount"
                                          />
                                      <FormLabel id="demo-radio-buttons-group-label">Condition</FormLabel>
                                        <RadioGroup
                                            aria-labelledby="demo-controlled-radio-buttons-group"
                                            name="controlled-radio-buttons-group"
                                            value={newAlertData['threshold_condition']}
                                            onChange={(e) => addDataToAlert('threshold_condition',e.target.value)}
                                          >
                                            <FormControlLabel value="increase" control={<Radio />} label="Percent Increase" />
                                            <FormControlLabel value="decrease" control={<Radio />} label="Percent Decrease" />
                                          </RadioGroup>
                                    </div>
                              }

    let formBody = additionalFormFields[type]
    setFormFields(formBody)
  }


  useEffect(() => {
    let requiredFields = ['alert_type', 'threshold', 'threshold_condition']
    let alertFields = Object.keys(newAlertData)
    console.log(alertFields)
    const enableSave = requiredFields.every(e => alertFields.includes(e))
    if (enableSave) setEnableSaveButton(true)
  }, [newAlertData]);

  const addDataToAlert = (test, value) => {
    const updatedValue = {}
    updatedValue[test]=value
    setNewAlertData(newAlertData => ({
      ...newAlertData,
      ...updatedValue
    }));
  }

  const saveAlert = (e) => {
    e.preventDefault();
    addDataToAlert('coin_sym',coinInfo.coinpair_sym)
    console.log(newAlertData)

    fetch('http://localhost:5000/alerts',{
      mode: 'no-cors',
      method: 'POST', // or 'PUT'
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(newAlertData),
    })
    //Todo: to check if the call was actually successful
    setSuccessSave(true)
  }

  const handleAlertChange = (e) =>{
    const value = e.target.value
    setNewAlertData({})
    addDataToAlert('alert_type',value)
    rebuildForm(value)
    setAlertType(value)
  }

    const modalContent = show ? (
      <StyledModalOverlay>
        <Snackbar open={successSave} autoHideDuration={6000} anchorOrigin={{ vertical: 'top', horizontal: 'center' }}  onClose={() => {setSuccessSave(false)}}>
              <Alert severity="success" sx={{ width: '100%' }}>
                Alert Saved!
              </Alert>
            </Snackbar>
        <StyledModal>
          <StyledModalHeader>
            <a href="#" onClick={handleCloseClick}>x</a>
          </StyledModalHeader>
          <div>Alert Creation</div>
          <StyledModalBody>From Alert creation modal
            <div>
              SYM:{coinInfo.coinpair_sym}
              Current Price:{coinInfo.price_value}
              Price Time:{coinInfo.price_update}
            </div>
            <div>
              <label for="coinSym">SYM:{coinInfo.coinpair_sym}</label>
              <form onSubmit={saveAlert} method="post">
              <FormControl sx={{ m: 1, minWidth: 120 }} required>           
                <InputLabel id="select-alert-label">Alert Type</InputLabel>
                <Select
                  labelId="select-alert-label"
                  id="alert-select"
                  label={alertType}
                  onChange={handleAlertChange}
                >
                  <MenuItem value="price">Price Alert</MenuItem>
                  <MenuItem value="percent">Percent Change Alert</MenuItem>
                </Select>
                </FormControl>
                <div>
                  {formFields}
                </div>
                <Button variant="contained" color="success" type="submit" disabled={!enableSaveButton}>Save Alert</Button>
              </form>
            </div>
            
          </StyledModalBody>
        </StyledModal>
      </StyledModalOverlay>
    ) : null;
  
    if (isBrowser) {
      return ReactDOM.createPortal(
        modalContent,
        document.getElementById("modal-root")
      );
    } else {
      return null;
    }
  };
  
  const StyledModalBody = styled.div`
    padding-top: 10px;
  `;
  
  const StyledModalHeader = styled.div`
    display: flex;
    justify-content: flex-end;
    font-size: 25px;
  `;
  
  const StyledModal = styled.div`
    background: white;
    width: 500px;
    height: 600px;
    border-radius: 15px;
    padding: 15px;
  `;
  const StyledModalOverlay = styled.div`
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
    background-color: rgba(0, 0, 0, 0.5);
  `;
  
  export default Modal;