import React, { useEffect, useRef, useState } from "react";
import ReactDOM from "react-dom";
import styled from "styled-components";
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

      console.log('here')
      let formBodyFields = {'price': 
                              {'priceValue':{
                                'label':<div>Price Value</div>,
                                'input':<div><input type="text"id="last"name="last" onChange={(e) => setNewAlertData['threshold']=e.target.value}/></div>},
                              'priceCondition': {
                                'label': <div>Condition</div>,
                                'input':<fieldset id="group2">
                                          <div style={{display:"flex",flexDirection:"column"}}>
                                            <label>
                                              <input type="radio" value="above" name="group2" onClick={(e) => {setNewAlertData['threshold_condition']=e.target.value}}/>Above Price
                                            </label>
                                            <label>
                                              <input type="radio" value="below" name="group2" onClick={(e) => {setNewAlertData['threshold_condition']=e.target.value}}/>Below Price
                                            </label>
                                          </div>
                                        </fieldset>}
                              }
                            }
    
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
                <label>Alert Type</label>
                <select  onClick={e => {setNewAlertData={}; setNewAlertData['alert_type']=e.target.value; rebuildForm(e.target.value)}}>
                  <option disabled selected value> -- select an option -- </option>
                  <option value="price">Price Alert</option>
                  <option value="percent">Percent Change Alert</option>
                </select>
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