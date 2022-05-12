import Image from'next/image'
import styles from './card.module.css'
import Link from 'next/link'
import Modal from '../modal';
import Paper from '@mui/material/Paper';
const {useEffect} = require("react");
const {useState} = require("react");
import {API} from "../../config"

function Card (props){
  const [showModal, setShowModal] = useState(false);
  const [src, setSrc] = useState(`/images/${props.coinpair_sym.split('-')[0].toLowerCase()}.png`);

  let coinpairImagePath = `/images/favicon.ico`


  let watchlistAction = (action) =>{
    let validActions = ['add','remove']
    if (!validActions.includes(action)){
      alert('error performing watchlist action')
      return
    }

    let body = {'user_id':'1','entity_type':'coin','entity_id':props.coinpair_id}
    fetch(`http://${API}/watchlist/${action}`,{
      mode: 'no-cors',
      method: 'POST', // or 'PUT'
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    })

    props.updateWatchlist(action,props.coinpair_id)
  }
  
    return (

        <Paper className={styles.card} elevation={4}>
          <Link href={"/coinpair/" + props.coinpair_id}>
            <div>
              <div className={styles.icon}>
                <Image
                  src={src} // Route of the image file
                  height={144} // Desired size with correct aspect ratio
                  width={144} // Desired size with correct aspect ratio
                  alt="Your Name"  
                  onError={() => setSrc(coinpairImagePath)}
                />
              </div>
            <div>SYM: {props.coinpair_sym}</div>
            <div>Last Update: {props.price_update}</div>
            <div>Price: {props.price_value}</div>
            </div>
            </Link>
            <div>
              <button onClick={() => setShowModal(true)}>Create Alert</button>
              {!props.watchlisted ? <button onClick={() => watchlistAction('add')}> Add to Watchlist</button> :
                  <button onClick={() => watchlistAction('remove')}> Remove from Watchlist</button>
              }
            </div>
              {showModal? <Modal
                onClose={() => setShowModal(false)}
                show={showModal}
                coinInfo={props}
                    >
              Hello from the modal!
            </Modal> : "" }
        </Paper>
      
  )
}
export default Card