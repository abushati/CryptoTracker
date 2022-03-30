import Image from'next/image'
import styles from './card.module.css'
import Link from 'next/link'
import Modal from '../modal';
const {useEffect} = require("react");
const {useState} = require("react");

function Card (props){
  let watchlistAction = (action) =>{
    let body = {'user_id':1,'entity_type':'coin','entity_id':props.coinpair_id}

    fetch(`http://localhost:5000/watchlist/${action}`,{
      mode: 'no-cors',
      method: 'POST', // or 'PUT'
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    })
  }


  const [showModal, setShowModal] = useState(false);
    return (
      
        <div className={styles.card}>
          <Link href={"/coinpair/" + props.coinpair_id}>
            <div>
            <Image
              src="/images/cardano.png" // Route of the image file
              height={144} // Desired size with correct aspect ratio
              width={144} // Desired size with correct aspect ratio
              alt="Your Name"
            />
            <div>SYM: {props.coinpair_sym}</div>
            <div>Last Update: {props.price_update}</div>
            <div>Price: {props.price_value}</div>
            </div>
            </Link>
            <div>
              <button onClick={() => setShowModal(true)}>Open Modal</button>
              {!props.watchlisted ? <button onClick={() => watchlistAction('add')}> Add to Watchlist</button> :
                  <button onClick={() => watchlistAction('remove')}> Remove from Watchlist</button>
              }
              <Modal
                onClose={() => setShowModal(false)}
                show={showModal}
                coinInfo={props}
                    >
               Hello from the modal!
            </Modal>
            </div>
        </div>
      
  )
}
export default Card