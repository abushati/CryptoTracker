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
//https://devrecipes.net/modal-component-with-next-js/
let setNewAlertData = {}
const Modal = ({ show, onClose, coinInfo }) => {
    const [isBrowser, setIsBrowser] = useState(false);
    const [alertType, setAlertType] = useState("");   
    const [formFields, setFormFields] = useState ([])
    // const [newAlertData, setNewAlertData] = useState({})

    
    useEffect(() => {
      setIsBrowser(true);
    }, []);
  
    const handleCloseClick = (e) => {
      e.preventDefault();
      onClose();

    };


  const rebuildForm = (alertType) => {
      let type = alertType
      if (type != 'price') {
        setFormFields([])
        return
      }
  //   'label':<InputLabel htmlFor="outlined-adornment-amount">Amount</InputLabel>,
                              //   'input': <OutlinedInput
                              //               id="outlined-adornment-amount"
                              //               value={0}
                              //               onChange={(e) => setNewAlertData['threshold']=e.target.value}
                              //               startAdornment={<InputAdornment position="start">$</InputAdornment>}
                              //               label="Amount"
                              //             />
                              // },
      console.log('here')
      let formBodyFields = {'price': 
                              {'priceValue':{
                                'label':<InputLabel htmlFor="outlined-adornment-amount">Amount</InputLabel>,
                                'input': <OutlinedInput
                                            id="outlined-adornment-amount"
                                            value={setNewAlertData['threshold']}
                                            onChange={(e) => setNewAlertData['threshold']=e.target.value}
                                            startAdornment={<InputAdornment position="start">$</InputAdornment>}
                                            label="Amount"
                                          />
                              },
                              'priceCondition': {
                                'label':<FormLabel id="demo-radio-buttons-group-label">Condition</FormLabel>,
                                'input':  <RadioGroup
                                            aria-labelledby="demo-controlled-radio-buttons-group"
                                            name="controlled-radio-buttons-group"
                                            value={setNewAlertData['threshold_condition']}
                                            onChange={(e) => {setNewAlertData['threshold_condition']=e.target.value}}
                                          >
                                            <FormControlLabel value="above" control={<Radio />} label="Above Price" />
                                            <FormControlLabel value="below" control={<Radio />} label="Below Price" />
                                          </RadioGroup>

                              }
                            }}
    
    let formBody = formBodyFields[type]
    let html = []
    Object.keys(formBody).map((field) => {       
      html.push(formBody[field]['label'])
      html.push(formBody[field]['input'])
    })
    console.log(html)
    setFormFields(html)
  }

  const saveAlert = (e) => {
    e.preventDefault();
    setNewAlertData['coin_sym']=coinInfo.coinpair_sym
    console.log(setNewAlertData)
    alert('saving alert')
    fetch('http://localhost:5000/alerts',{
      mode: 'no-cors',
      method: 'POST', // or 'PUT'
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(setNewAlertData),
    })
  }

  const handleAlertChange = (e) =>{
    const value = e.target.value
    setNewAlertData={}
    setNewAlertData['alert_type']=value
    rebuildForm(value)
    setAlertType(value)
  }

    const modalContent = show ? (
      <StyledModalOverlay>
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
                  {formFields.map(field => field)}
                </div>
                <button type="submit">Save Alert</button>
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