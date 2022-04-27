import styles from './alertCard.module.css'

export const AlertCardType = Object.freeze({
  INFO : 'INFO',
  GENERATION : 'GENERATION'
})


function AlertCard (props){
    let cardHeader = props.cardHeader
    let cardBody = props.cardBody
    let type = props.type

    const getClassname = () => {
      if (type == AlertCardType.GENERATION){
        return styles.generatedAlert
      }
      else if (type == AlertCardType.INFO){
        return styles.alert
      } 
    }

    return (      
        <div className={getClassname()}>
          <div>
            {cardHeader}
          </div>
          <div>
            {cardBody}
          </div>
        </div>
  )
}
export default AlertCard