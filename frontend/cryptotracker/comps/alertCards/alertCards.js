import styles from './alertCard.module.css'
import { API } from '../../config';
import { Card } from '@mui/material';
// import '@fortawesome/fontawesome-free/css/all.css';
import Modal from '../modal';

const {useState} = require("react");



export const AlertCardType = Object.freeze({
  INFO : 'INFO',
  GENERATION : 'GENERATION'
})

export const CardActions = {
  DELETE : 'DELETE',
  MARK_READ : 'MARK_READ',
  EDIT : 'EDIT'
}

let cardActions = {
  'INFO': [CardActions.DELETE, CardActions.EDIT],
  'GENERATION':[CardActions.MARK_READ]
}

function AlertCard (props){
    const [showModal, setShowModal] = useState(true);
    const [showActions, setShowActions] = useState(false)
    let cardHeader = props.cardHeader
    let cardBody = props.cardBody
    let type = props.type
    let actions = cardActions[type]
    let id = props.id
    let alertData = props.alertData
    

    const handleCardClick = () =>{
      if (showActions){
        setShowActions(false)
        return 
      }
      setShowActions(true)
    }

    const getClassname = () => {  
      if (type == AlertCardType.GENERATION){
        return styles.generatedAlert
      }
      else if (type == AlertCardType.INFO){
        return styles.alert
      } 
    }

    const handleActionClick = (e) => {
      
      console.log(`action ${e} on ${type} with id: ${id}`)
      if (type === AlertCardType.GENERATION){
        if (e === CardActions.MARK_READ){
          pass
        }
      } else if (type === AlertCardType.INFO){
          if (e === CardActions.DELETE){
            fetch(`http://${API}/alert/${id}`, 
            {
              method:'DELETE'
            });
          }
          else if (e === CardActions.EDIT){
            setShowModal(true);
          }
      }
    }

    const getActionButton = (action) => {

      let a = <div className={styles.action} onClick={() => handleActionClick(action)}>
          <i className="fas fa-envelope-open" key={Math.random()*1000}>{action}</i>
      </div>
      return a
    }

    return (      
        <div className={getClassname()} >
          <div className={styles.detailContainer} onClick={handleCardClick}>
            <div>
              {cardHeader}
            </div>
            <div>
              {cardBody.map(bodyPart => {
                return <div>{bodyPart}</div>
              })}
            </div>
          </div>
          <div className={`${styles.actions} ${showActions ? styles.showAction:""}`}>
            {
              actions.map(action => getActionButton(action))
            }
          </div>
          {showModal ? <Modal
                onClose={() => setShowModal(false)}
                show={showModal}
                coinInfo={props.coinInfo}
                alertInfo={alertData}
                    >
              Hello from the modal!
            </Modal> : "" }
        </div>
  )
}
export default AlertCard