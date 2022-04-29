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

    const handleActionClick = (e) => {
      console.log(e)
    }

    const getActionButton = (action) => {
      let a = <div className={styles.action} onClick={() => handleActionClick(action)}>
          <i className="fas light fa-envelope-open" style={{display: 'block',width: '100%',height: '100%'}} key={Math.random()*1000}></i>
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
              {cardBody}
            </div>
          </div>
          <div className={`${styles.actions} ${showActions ? styles.showAction:""}`}>
            {
              actions.map(action => getActionButton(action))
            }
          </div>
        </div>
  )
}
export default AlertCard