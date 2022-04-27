import styles from './alertCard.module.css'
const {useState} = require("react");

export const AlertCardType = Object.freeze({
  INFO : 'INFO',
  GENERATION : 'GENERATION'
})

export const CardActions = {
  DELETE : 'DELETE',
  MARK_READ : 'MARK_READ'
}

function AlertCard (props){
    const [showActions, setShowActions] = useState(false)
    let cardHeader = props.cardHeader
    let cardBody = props.cardBody
    let type = props.type
    
    
    let cardActions = {
      'INFO': [CardActions.DELETE],
      'GENERATION':[CardActions.MARK_READ]
    }

    const handleCardClick = () =>{
      if (showActions){
        setShowActions(false)
        return 
      }

      let actions = cardActions[type]
      console.log(actions)
      for (const action in actions){
        break
      }
    }

    const getClassname = () => {  
      if (type == AlertCardType.GENERATION){
        return styles.generatedAlert
      }
      else if (type == AlertCardType.INFO){
        return styles.alert
      } 
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
          <div className={styles.action}>
            test
          </div>
        </div>
  )
}
export default AlertCard