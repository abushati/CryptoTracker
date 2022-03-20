import React, { useEffect, useRef, useState } from "react";
import ReactDOM from "react-dom";
import styled from "styled-components";
//https://devrecipes.net/modal-component-with-next-js/
const Modal = ({ show, onClose, coinInfo }) => {
    const [isBrowser, setIsBrowser] = useState(false);
  
    useEffect(() => {
      setIsBrowser(true);
    }, []);
  
    const handleCloseClick = (e) => {
      e.preventDefault();
      onClose();
    };
  
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
              Alert Type
              <select>
                <option value="price">Price Alert</option>
                <option value="percent">Percent Change Alert</option>
              </select>
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