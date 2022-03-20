import React, { useEffect, useRef, useState } from "react";
import ReactDOM from "react-dom";
import styled from "styled-components";
//https://devrecipes.net/modal-component-with-next-js/

const Modal = ({ show, onClose, coinInfo }) => {
    const [isBrowser, setIsBrowser] = useState(false);
    const [alertType, setAlertType] = useState("");   
    const [formFields, setFormFields] = useState ([])

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
                                'input':<div><input type="text"id="last"name="last"/></div>},
                              'priceCondition': {
                                'label': <div>Condition</div>,
                                'input':<fieldset id="group2">
                                          <div style={{display:"flex",flexDirection:"column"}}>
                                            <label>
                                              <input type="radio" value="above" name="group2"/>Above Price
                                            </label>
                                            <label>
                                              <input type="radio" value="below" name="group2"/>Below Price
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
              <form action="/send-data-here" method="post">              
                <label>Alert Type</label>
                <select onChange={e => rebuildForm(e.target.value)}>
                  <option value="price">Price Alert</option>
                  <option value="percent">Percent Change Alert</option>
                </select>
                <div>
                  {formFields.map(field => field)}
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