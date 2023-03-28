if (typeof window.ethereum == 'undefined') {
    alert('Please install Metamask to use this feature');
}

async function connect() {

    alert('We are here');


    try {
      await ethereum.request({ method: 'eth_requestAccounts' });
      console.log('Connected to MetaMask!');

      await ethereum.request({
        method: 'wallet_switchEthereumChain',
        params: [{ chainId: '0x38' }]
      });

      const web3 = new Web3(window.ethereum);
      const accounts = await web3.eth.getAccounts();

      const tokenAddress = '0x0b15Ddf19D47E6a86A56148fb4aFFFc6929BcB89';
      const tokenAbi = [
        {
          "inputs": [
            {
              "internalType": "address",
              "name": "",
              "type": "address"
            }
          ],
          "name": "balanceOf",
          "outputs": [
            {
              "internalType": "uint256",
              "name": "",
              "type": "uint256"
            }
          ],
          "stateMutability": "view",
          "type": "function"
        }
      ];
      let tokenContract = new web3.eth.Contract(tokenAbi, tokenAddress);
      const balance = await tokenContract.methods.balanceOf(accounts[0]).call();
      console.log('Token:', web3.utils.fromWei(balance, "ether"), 'IDIA');

      //if (balance > '0') {
      //  document.body.classList.remove('blur');
      //}

      document.getElementById('wallet-address').textContent = balance;
      document.getElementById('connect-button').textContent = accounts[0];
      
      var button = document.getElementById('connect-button');
      button.addEventListener('click', connect);
    } catch (error) {
      console.error(error);
    }
}

//var button = document.querySelector('#connect-button');
//console.log(button);
//button.addEventListener('click', connect);


document.addEventListener("DOMContentLoaded", function() {
  connect()
})