import Paper from '@mui/material/Paper';


function AlertCard (props){
    let cardHeader = props.cardHeader
    let cardBody = props.cardBody
    
    
    // border: red;
    // border-style: dashed;

    return (      
        <Paper style={{}}>
          <div>
            {cardHeader}
          </div>
          <div>
            {cardBody}
          </div>
          </Paper>
  )
}
export default AlertCard