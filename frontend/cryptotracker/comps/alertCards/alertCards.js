import styles from './alertCard.module.css'
// import '@fortawesome/fontawesome-free/css/all.css';

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
    const [showActions, setShowActions] = useState(false)
    let cardHeader = props.cardHeader
    let cardBody = props.cardBody
    let type = props.type
    let actions = cardActions[type]
    

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

    const getActionButton = (action) => {
      let a = <div className={styles.action}>
          x
      </div>
      return a
    }

    return (      
        <div className={getClassname()} onClick={handleCardClick}>
          <div>
          <div>
            {cardHeader}
          </div>
          <div>
            {cardBody}
          </div>
          </div>
          {/* {showActions ?  */}
            <div className={`${styles.actions} ${showActions ? styles.showAction:""}`}>
              {
                actions.map(action => getActionButton(action))
              }
            </div>
            {/* : '' */}
          {/* } */}
        </div>
  )
}
export default AlertCard