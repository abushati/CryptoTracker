import { API } from "../config";

import React, { useEffect, useRef, useState } from "react";
import ReactDOM from "react-dom";
import styled from "styled-components";
import MenuItem from '@mui/material/MenuItem';
import Select from '@mui/material/Select';
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
const Modal = ({ show, onClose, coinInfo, alertInfo=null }) => {
    const [isBrowser, setIsBrowser] = useState(false);
    const [alertType, setAlertType] = useState("");   
    const [formFields, setFormFields] = useState ([])
    const [newAlertData, setNewAlertData] = useState({})
    const [enableSaveButton, setEnableSaveButton] = useState(false)
    const [showSnackBar, setShowSnackBar] = useState(false)
    const [snackBarInfo, setSnackBarInfo] = useState({})

    const Alert = React.forwardRef(function Alert(props, ref) {
      return <MuiAlert elevation={6} ref={ref} variant="filled" {...props} />;
    });
    
    const addDataToAlert = (test, value) => {
      const updatedValue = {}
      updatedValue[test]=value
      setNewAlertData(newAlertData => ({
        ...newAlertData,
        ...updatedValue
      }));
    }


    if (alertInfo) {
      addDataToAlert('threshold',alertInfo.threshold)
      addDataToAlert('threshold_condition',alertInfo.threshold_condition)
      // addDataToAlert('notification_settings_method',alertInfo)
      // addDataToAlert('notification_settings_value',alertInfo.threshold)
      addDataToAlert('alert_type',alertInfo.alert_type)
      
    }

    useEffect(() => {
      console.log('handle mount')
      setIsBrowser(true);
    }, []);
  
    const handleCloseClick = (e) => {
      e.preventDefault();
      setNewAlertData({})
      setFormFields([])
      setAlertType("")
      setEnableSaveButton(false)
      setShowSnackBar(false)
      onClose();

    };

  useEffect(()=>{
    if (isBrowser) {
      addDataToAlert('coin_sym',coinInfo.coinpair_sym)}
  },[isBrowser])

  const rebuildForm = (alertType) => {
      let type = alertType
      let additionalFormFields = {'price': 
                                    <AdditionalModelFields>
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
                                      </AdditionalModelFields>,
                                     
                                'percent':
                                  <AdditionalModelFields>
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
                                    </AdditionalModelFields>
                              }

    let formBody = additionalFormFields[type]
    let notificationBody = <AdditionalModelFields>
                                    <FormLabel id="demo-radio-buttons-group-label">Notication Settings (optional)</FormLabel>
                                    <FormLabel id="demo-radio-buttons-group-label">Notication method (optional)</FormLabel>
                                    <RadioGroup
                                            aria-labelledby="demo-controlled-radio-buttons-group"
                                            name="controlled-radio-buttons-group"
                                            value={newAlertData['notification_settings_method']}
                                            onChange={(e) => addDataToAlert('notification_settings_method',e.target.value)}
                                          >
                                            <FormControlLabel value="email" control={<Radio />} label="Email" />
                                            <FormControlLabel value="sms" control={<Radio />} label="SMS" />
                                          </RadioGroup>                                    
                                    <InputLabel htmlFor="outlined-adornment-amount">Notication Destination</InputLabel>
                                    <OutlinedInput
                                            id="outlined-adornment-amount"
                                            value={newAlertData['notification_settings_value']}
                                            onChange={(e) => addDataToAlert('notification_settings_value',e.target.value)}
                                            startAdornment={<InputAdornment position="start"></InputAdornment>}
                                            label="Amount"
                                          />
                            </AdditionalModelFields>
                            
    
    let form = <div>
                {formBody}
                {notificationBody}
              </div>

    setFormFields(form)
  }


  useEffect(() => {
    let requiredFields = ['alert_type', 'threshold', 'threshold_condition']
    //TODO: check if notication is filled out
    let alertFields = Object.keys(newAlertData)
    const enableSave = requiredFields.every(e => alertFields.includes(e))
    if (enableSave) setEnableSaveButton(true)
  }, [newAlertData]);

  const showSnack = (success)=>{
    if (success){
      var msg = 'Alert Saved!'
      var type = 'success'
    }
    else {
      var msg = 'Failed To Save Alert!'
      var type = 'error'
    }

    const updatedValue = {}
    updatedValue['msg']=msg
    updatedValue['type']=type
    setSnackBarInfo(snackBarInfo=>({...snackBarInfo,...updatedValue}))
    setShowSnackBar(true)
  }

  const saveAlert = (e) => {
    e.preventDefault();
    let data = newAlertData
    data['coin_sym']=coinInfo.coinpair_sym
    fetch(`http://${API}/alerts`,{
      // mode: 'no-cors',
      method: 'POST', // or 'PUT'
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(newAlertData),
    }).then(res =>{
      if (res.status == 200){
        showSnack(true)
      }
      else{
        showSnack(false)
      }
      console.log(res.status)
    })
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
        <Snackbar open={showSnackBar} autoHideDuration={6000} anchorOrigin={{ vertical: 'top', horizontal: 'center' }}  onClose={() => {setShowSnackBar(false)}}>
              <Alert severity={snackBarInfo.type} sx={{ width: '100%' }}>
                  {snackBarInfo.msg}
              </Alert>
            </Snackbar>
        <StyledModal>
          <StyledModalHeader>
            <div style={{width:"85%"}}>Alert Creation</div>
            <a href="#" onClick={handleCloseClick}>x</a>
          </StyledModalHeader>
          <StyledModalBody>
            <div style={{fontSize:"1.2em",padding:'10px 0px'}}>
              <div>SYM:{coinInfo.coinpair_sym}</div>
              <div>Current Price:{coinInfo.price_value}</div>
              <div>Price Time:{coinInfo.price_update}</div>
            </div>
            <div>
              <form onSubmit={saveAlert} method="post">
                <Hi >
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
                  </Hi>
                  <div style={{padding:'10px 0px',display:'flex',justifyContent: 'center'}}>
                  <Button variant="contained" color="success" type="submit" disabled={!enableSaveButton}>Save Alert</Button>
                  </div>
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
  
  const Hi = styled.div`
  max-height: 400px;
  overflow: scroll;
`;
  const StyledModalBody = styled.div`
      padding:'10px'
  `;
  
  const StyledModalHeader = styled.div`
    display: flex;
    font-size: 25px;
    border-bottom: gray;
    border-width: thin;
    border-bottom-style: solid;
    padding-bottom: 10px;
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
  
  const AdditionalModelFields = styled.div`
  display: flex;
  flex-direction:column;
`;

  export default Modal;