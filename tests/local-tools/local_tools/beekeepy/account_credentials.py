from __future__ import annotations

import random
from typing import Final

from beekeepy.interfaces import KeyPair

ACCOUNTS_DATA: Final[list[dict[str, str]]] = [
    {
        "private_key": "5HyrZRsejVQWns9QFtTXZPMXeopTK7GUpHx2Sy1qD2omayn3LS4",
        "public_key": "STM82ntKLzbYi8vgYvZFwRWX8iC8b3aChsp1y7YufiZfyLAs3eQ1Q",
        "account_name": "account-0",
    },
    {
        "private_key": "5KE321Buyp5ZRQ4DhetxjuBkekcknLwbW1LNLUt3UtQ5CjWMGzh",
        "public_key": "STM6CUYDwRY2nrC8m3H78HpdGFoA1Fp5vQ7pivNFoUcmLwyxpSgde",
        "account_name": "account-1",
    },
    {
        "private_key": "5KRJixCyjjmQePaG9zSMiRxcc6xPGmADuCXLxkjotztML6y6zvK",
        "public_key": "STM6kNKZQ5kxJsrUdMMufSJpoWCrwaFj1rYZJfd4RnjcNw4GGwyFY",
        "account_name": "account-2",
    },
    {
        "private_key": "5JsPjhAFccR9gkJYgMdA6TA6Dt3E9qV3LN1CoqpQJAYGt5jC1Um",
        "public_key": "STM8FXEeK9edTTKaY6aB2VfhCv8dDweMWs6hk5fhkG11BM6AuosyN",
        "account_name": "account-3",
    },
    {
        "private_key": "5K9fVKHtb1uk2NaGDgUyDjH7hBcRFAwEDiXRrRTijvzdu42cCMQ",
        "public_key": "STM6E4w4QJxFwyPixTqAx9GBdV72HNj5FVzNtoWA36y9hP3VEkP4u",
        "account_name": "account-4",
    },
    {
        "private_key": "5JG41mHyH8ZbnmYepRnxNLhBZBMGPBuzaED2vkSS2HXaw8PfKzP",
        "public_key": "STM7T9s6XQWWswidguTky8oCu5yvpMZQQ8SQDVPprnyg8N2LL67hs",
        "account_name": "account-5",
    },
    {
        "private_key": "5JX3JzmUsEHCZLvSLcyT2pqCFGZTrhPj4ob6ewhXV5G8XXgKFDh",
        "public_key": "STM81CBAKqkPRfLQrTXr4esxbu6Zn3xLnqeRHnytz4LNmvsWJ37Lv",
        "account_name": "account-6",
    },
    {
        "private_key": "5JEV7t2xZ2hvJheLmA9ZhFj44ycXxfcPDTvM2wWfo489sxYuSQx",
        "public_key": "STM7GZGuVRVZ3XUkaQCm4F5abvsrTBrhV9P4FG8XyP5fMzMWnKpm9",
        "account_name": "account-7",
    },
    {
        "private_key": "5Jff3UYKEv9EnRWj5hu75bTK1tnD9gEqXtLwJ3q44qXR6SrSKq6",
        "public_key": "STM6YpeBVhYappteeqxAHqpoZAncJRpTkUZhteNiRfxhPYHjZa6h4",
        "account_name": "account-8",
    },
    {
        "private_key": "5Jd76MCvKfv2DAztK86GR4ETdiDM9BD3RAJ8vmV8p1n6J1k6tXF",
        "public_key": "STM63kZLfJX4Qi8xzm5DtSzgi7JVRjkak8w1Kb5ZiwagHJYCSbP3k",
        "account_name": "account-9",
    },
    {
        "private_key": "5HsQRmMjHKxkivLie2XFjScqa87ta14dbF4sNxfvjAnmgszHp4K",
        "public_key": "STM8LsSm6s8J9r8sfnC6xiViTkTVpneDmuCwbkdBZSNWjqDSwWHwa",
        "account_name": "account-10",
    },
    {
        "private_key": "5KZdsnmmgzaB8sMpw2yAmjgTxMYjRJWQp9w3fLAUcRJHYUNFsCa",
        "public_key": "STM7LWb3MrKuiVKsc4XAC6zDfKoEfuJ5hgRVpmZ1dqQh7ALC543eq",
        "account_name": "account-11",
    },
    {
        "private_key": "5JHkH21ybyK3opD42CHuBwJDe6L7Mc5UXNjwec4f1vNW4Gijgxs",
        "public_key": "STM89P7cNXmhjmJeFDdgidCpay6hzdxJqgyyF2jJDtcXuCyvt2tyn",
        "account_name": "account-12",
    },
    {
        "private_key": "5J6jqBuCXUxYHFD7CHjkdebyKRDqJmFXGREeBayCumGtB78r7ff",
        "public_key": "STM7DLqJwZCkKHcLYz3S4FssaWFMFnpKZ4SnJBQMCpyauRkfjRHKL",
        "account_name": "account-13",
    },
    {
        "private_key": "5JP8a7CAqkMGAESSaXWEHUVdHJsPwzdSBn4EN3EvbHwZRcmffPB",
        "public_key": "STM6iHftppLZpoFL9yR8XGTcF1CLxCYsn2vFZda7ioCrqGWFnaN7W",
        "account_name": "account-14",
    },
    {
        "private_key": "5Jk5VFnLzZPHUVkUhT9ba6vfmPcsNy8A21MG4cbiP5Fc3g42ihe",
        "public_key": "STM4ue4CJwWAbBech5Z7dr5AziJk7eJhnTHbNCff8QkXQZStnnwsZ",
        "account_name": "account-15",
    },
    {
        "private_key": "5HyxSCUncHiFwmPMWxLS4EhC46TjZGDGroythNgMLiBBJuQiZ8C",
        "public_key": "STM6Hq6uKsV4jBpDxjp9E7fTpsp9MsLd7mKaNwnAX2MU1LPfWJyJq",
        "account_name": "account-16",
    },
    {
        "private_key": "5JaGswLAX5Vfk4seRAbY6m7hknkBj8QVV8Zp14y5hkjeJBs7i4d",
        "public_key": "STM7GVcJ31F4uBZuVa7MnUSN5qJrtUG82yPqc2ua8c7YEgHiC2qq1",
        "account_name": "account-17",
    },
    {
        "private_key": "5HpeGc2JzHeXJFpCcXaE5v5zvfkAN3rAq3L4EEg6DHbEQWWnYb3",
        "public_key": "STM5DrY3Ev4BHPyf6MFPAohQHxqNv3HufazFLVBxVdHnmqFrK2tN4",
        "account_name": "account-18",
    },
    {
        "private_key": "5JQERr7ypDp3ayN464pdQyNBZ6VnUT9bzqMUFGmJgpyeUAUmYLi",
        "public_key": "STM8k1FB5Uyakk58gALxVcMeuBm3i1yDMq7Fpia9WQfmSxZ3veALQ",
        "account_name": "account-19",
    },
    {
        "private_key": "5JXjKtv9qhvhPTEThDRj1Jn2uR6C8XfyDX2hZNfsn6gN4ARPqR7",
        "public_key": "STM5cBXU7zzprt9mQwktiPJccL2hNrUked9q2KztAeQux6zPYq6np",
        "account_name": "account-20",
    },
    {
        "private_key": "5K9WVYVcQZV8VMRZbnsxk6epc5HJ7p6dKeqvLyWEBTChSzpYnw3",
        "public_key": "STM7rDWhkPwz361xHUqjiy44qvRweGDDR2Darnvn2UHb2oMB4owsP",
        "account_name": "account-21",
    },
    {
        "private_key": "5JJnvC4gGmxTC7qpo7xAUwuTQcwVmZpBZsgLeYZBAqe7F1Kf2pe",
        "public_key": "STM8GGjPHzBCiDZucsGeeWoZFxbcuxg2NeR5eVofSqCWPGTPNB3gC",
        "account_name": "account-22",
    },
    {
        "private_key": "5JEo7yGJN6TCwbmgQM3UNZkqnsGi5aWTX48FeskCaawRJ2mZJ2M",
        "public_key": "STM6LyoAoQ5gjwNwXKQgiAawSBUno4nCDT6385Jqgbp1U7iQ17Tci",
        "account_name": "account-23",
    },
    {
        "private_key": "5KRSM7Bryji2TPyfKCpeDMcyiDqkvpqHHLqVQgaDioFymyxn7Ri",
        "public_key": "STM7GCQSKZDTMH1b4Gi48wd243L8EPwexVSLZmLTdvfjXnVfppi5H",
        "account_name": "account-24",
    },
    {
        "private_key": "5JkPEqpYYVJUsbKJzUEqbpum1AA4ZLsUPJgPX6TUJEUPWdWsUdd",
        "public_key": "STM69GVYU3DDc84eNpapx58wRs6HDW6qbvANzgwK1y1uj2NRwRLmA",
        "account_name": "account-25",
    },
    {
        "private_key": "5HxtUksEejv3Nwqdd273ZRRR1AVtSgZbAMB3i8fTs5EYBAEkGh1",
        "public_key": "STM6HC1LAQekCWC2rhwvGfJRg9jwRUJafeqfMU6QYAJgGFciT4yJp",
        "account_name": "account-26",
    },
    {
        "private_key": "5JDZQJJ7UX6HfF4kyuNYRTqzw4WFRx33Ugeji2fVmqxa44UuqsT",
        "public_key": "STM59FWVAVdqgRa2b8BF7pDm1BB5ReteiDL3xhQtW3sqjjPCwUcHy",
        "account_name": "account-27",
    },
    {
        "private_key": "5JTVNsLjTjZDWHDq5MShs4i9svc1X3HJ2UCMTjjMvDudNicSJf2",
        "public_key": "STM6tXepUeYjb3wj1ERz4Hj26VCFuSCZQgiUMHhp4suiZAHTFXiFs",
        "account_name": "account-28",
    },
    {
        "private_key": "5JzQ1HTmJPaDpWpRFtbQ8hEjaX82fBmPEs7GPUzp3EXH1GtdGT9",
        "public_key": "STM6D9RuCeHQZH6MqoNzxhY2kkH6dBzpx96yYKzjcBmKZGg7U6wBA",
        "account_name": "account-29",
    },
    {
        "private_key": "5Jsos1GvWwVzPCYvqjQPWVHTuGj3Hi7dhMSsb3XwgDXNpQsbAoX",
        "public_key": "STM5FVNcd74RwrEECXiXv89Swdw9DzdJTWaACxhuT8aF8pWRGeQjE",
        "account_name": "account-30",
    },
    {
        "private_key": "5JLZbTXbD4kUbxBXi3GhQvxksYDDFmJCWusrDtTyZBgAZSMmg72",
        "public_key": "STM7UXciojf3FT8EEkyVa5rHraiLNi4ZJVRDVjee7TsReyuzUzeNe",
        "account_name": "account-31",
    },
    {
        "private_key": "5JQiqdqyrTmaBFL1hi7hic2hbF2Mo78kuz8s9X4aKALae4j6o8k",
        "public_key": "STM8g7WCmRGLrdcZZCbWsUaWGArYLGj6fpkKnb6xKEzzUcyhCdPrk",
        "account_name": "account-32",
    },
    {
        "private_key": "5KN7ktJjqkKx5pUdG6EX2i9Mza5N2Hs83qHVy7LayudYptXvmLi",
        "public_key": "STM4w4xoBDDQKJHSkWQtCV3yhtN3VS8cYkswUxtjF6YxCrs1PsJVd",
        "account_name": "account-33",
    },
    {
        "private_key": "5KMAzFcHxhyRV1QGorto7rcNuUs1PsKWZjgoJqRPD9b71WYYBy9",
        "public_key": "STM6hpfeYSrnaB1P4xkR5En2KRmZ71HjXeDgkyZABshBpDqvs9c5H",
        "account_name": "account-34",
    },
    {
        "private_key": "5KKNJCzYrBrSCXd2G3UJX9TpPgG9H5iAYZa8XfXmdoTKcCVsGhE",
        "public_key": "STM6NVKdroEDBsDqwYz7DS7SzBJt8JWPiLhs1nGCJbLouDVyhRyjK",
        "account_name": "account-35",
    },
    {
        "private_key": "5Jf2AynonkRQPP6d3mmZjFbrhY1FnLt2x1aLKgyFJMFkooN4xhA",
        "public_key": "STM5NPWS6viRduE9MoKfe5aFUKMgTsawzpnT5KtKiFdgZ8TqKMGeW",
        "account_name": "account-36",
    },
    {
        "private_key": "5KVAbi1C32EpXVDFNSNVDw8BYAmhuQgx4GERCDh4nRbCh8dhKN4",
        "public_key": "STM87u15qFhYFbpxNx2Bf9xF1YJguMbP5KRmL5LNRz8Ky1TVns8LA",
        "account_name": "account-37",
    },
    {
        "private_key": "5J9TZS4RWoF4umbnGgVEPSRjYXLfRuf1Y57uCxSoREmftSRR8Sv",
        "public_key": "STM6ucZ6rV3jEZvnqVkcfk6eu3ij4FiwqicSk3taeFo3UkyzPraXR",
        "account_name": "account-38",
    },
    {
        "private_key": "5K4QckBje4wAwebB7D2J7vjeMmZ69SiFnCXfcZREyUE15maWTSg",
        "public_key": "STM5xAPePNdP3b4kPwDPrEJ7QXkew4LPp9XEmSnXZK7Pi5MaYE5YF",
        "account_name": "account-39",
    },
    {
        "private_key": "5HwpmvU5PwLSm61qGCnbsZJDG3Gka6RATuS8Jfvtp5YYhCoxxNV",
        "public_key": "STM8GXBUUAENmDcf1diwyvSoCmLf83c5YkhMJtSFwTNnzvg3XkGxt",
        "account_name": "account-40",
    },
    {
        "private_key": "5HsQKoZs78edV9ZJeygKehb6qnefdfHduuD2oJQuoMnAYo3rU8Q",
        "public_key": "STM7TihvhcHM9eQicp7N7iPbMd4gwEXtNoQKBvckfYhxWaDVMrhvN",
        "account_name": "account-41",
    },
    {
        "private_key": "5KjzPNJ9sDYDQMcDG6RBUYgMNDVTYdVcKAHUDwRM4YQDRwVyGZ6",
        "public_key": "STM6wGeu77VqqVK3Jt2xY2f8RCzm9ZWCvsFzd6wxPMh7t9WmnAkSk",
        "account_name": "account-42",
    },
    {
        "private_key": "5HuDgKPyqypfa7h6AmTbUxVLGAfXTt9XKsYVQFf5g37hdiwbZkJ",
        "public_key": "STM8ZBsRvDMCdc7bthTKsyE9EJGMXzaU3y41jdysWbbfy6j5tgkR7",
        "account_name": "account-43",
    },
    {
        "private_key": "5Hz3QmiZhDm1RWxVPc7UrXU92Q29YAvNiYE5XpiFGYziB7FPtix",
        "public_key": "STM5g1qEqw3qHT3C7LLzcaPi9ptacJhC46WEByF5BBXCxJR79m3xS",
        "account_name": "account-44",
    },
    {
        "private_key": "5J418EySwQEzKE7jAuyBVZ2td5dvE4SHr9Tcq85vW4BK2GHNz9t",
        "public_key": "STM5gyhooLmQdotryux8cXCbtuBoUq4f4dCNkAM8BeU39h7aC5Zn7",
        "account_name": "account-45",
    },
    {
        "private_key": "5KFFcwbSLi4jSksCcaPYnQqVpMKjktZJPmqwUspjqJX6tp1b3zw",
        "public_key": "STM6hBaSk9ikpWNXvgYEp7nsEn9MmkrRFNAFpsR8HtxCBbq9LTsUH",
        "account_name": "account-46",
    },
    {
        "private_key": "5JTM2CJmiLcErXcsRXSe59NXbAufaJBHy1Xa9LdV1kPuvrN7XSK",
        "public_key": "STM6wzFw6DrkPxvnqMtjvxhyrEMLJ3Wf9re7a6zzmhK6Ex5be7UkG",
        "account_name": "account-47",
    },
    {
        "private_key": "5KEWKwRoenmPf4BsSSScGQHsVqpuLH5kYY5harsZLrZyiTsxo3L",
        "public_key": "STM5zi342nrNwTMDxDVJgPbxk9m6Ua3AjEPD5JdC3bCAXWVNhgmVd",
        "account_name": "account-48",
    },
    {
        "private_key": "5K2jub1xMiMBxUz525rV2YuoDLUswHxHGNNJRnMvivWsyr82wFP",
        "public_key": "STM567EM6mvRDSiUtNRTVNtgViPoeKDu1ScuRKYdX9jWyqRxXL6ux",
        "account_name": "account-49",
    },
    {
        "private_key": "5JDkWBgm4JdpaYgyAXAWvfVgucD8TzRubzaKCuvZ4ChPpHhWEac",
        "public_key": "STM5rG2aiBC7ZLMitpzntbq6rcpT5JrDRSzdBVjrPuaszNaMHaaG2",
        "account_name": "account-50",
    },
    {
        "private_key": "5JfALZ4UhFykVF9w5emxVnbzfRwxzf5yaBDMc75CEew8Mc1rypL",
        "public_key": "STM83suoHYzomT8Ns8PUwum3i3ow9MLJyvWWPBZTSekRqVVAtuYMi",
        "account_name": "account-51",
    },
    {
        "private_key": "5JaixGmSsf8WWSMs81ZNbozsk6ZhMm29bQTK45uhbpCV2E7TttW",
        "public_key": "STM5A4UFqhzv6nUzMMdRrmVJd9j7iHW7FXxPnzLd1o8Kunoqi29mT",
        "account_name": "account-52",
    },
    {
        "private_key": "5JDnPidRbGcTjSjZFagdEat3nTMd3UQgXrcH5kj5RJRjgtZJgSG",
        "public_key": "STM7dGoyQGFDCS3G3qgGSJoHnuTVVjAfCDhHtSnLEQtnMVv3pfaJi",
        "account_name": "account-53",
    },
    {
        "private_key": "5J9uKqiGAEBacXqgkttR8a4GHv9zzjgxAyv3u3d8bv7MibqhsBf",
        "public_key": "STM81RdgojtTUBexxA3UHMQTEWnmwhFP4EPctyW4f2fuSq5AQGMNd",
        "account_name": "account-54",
    },
    {
        "private_key": "5JMQuEGpg8aBtogF8aJRfgyy6XdYCA9NGzCtw88PkLbxGGbytYq",
        "public_key": "STM4zT2EAwwykPMFfggdEyqqZRoQnrDGdNCQCCFFd4qF6tG9yhLwA",
        "account_name": "account-55",
    },
    {
        "private_key": "5JutEpSfwp3tn61zQcRh1imPiPanrgM3yuHpNM1VEyqvZhEcUdn",
        "public_key": "STM8GKXZaWkY4ENxjmhwYDsiUhrapFUQos1jM8tkpv1g5TZFgxsrW",
        "account_name": "account-56",
    },
    {
        "private_key": "5Jmzumhzn62LbeUaGZLNZpfcKkiMQXWTRTdoheLFSxidtnePwua",
        "public_key": "STM7hxDubaqcoG41n79h4jxhYrPbLtDDyJPxVoenxrnx2MtqSyNRo",
        "account_name": "account-57",
    },
    {
        "private_key": "5JTeEKq5DjL1ZKvRZTLpNWAGgUqqhVNZCgLiyhduB8ugRbFSm46",
        "public_key": "STM6YHzEfuFpCroo1kyDB66zeu93yyqqE3mVcqFqbQDQx67uTL6G7",
        "account_name": "account-58",
    },
    {
        "private_key": "5KVDRsD1cjXMkUpUkwGj9NV9SxiaLhz1E3AhwrL85M4eS3PSXUy",
        "public_key": "STM5VGcLabiMRj7sHWNSb4qhZk8DPfrHoSTPppow3UbtGRxUDvfHe",
        "account_name": "account-59",
    },
    {
        "private_key": "5JxBmPDxo94jHjFE5aRcwkwLJ7SfnZR1iRBTQY1EQ3oUxraTNRB",
        "public_key": "STM68W4yCDAm4E5R3YfdrnNgRqF47ennJyMa82Y6dCaJVa2gz89Ap",
        "account_name": "account-60",
    },
    {
        "private_key": "5J6hKDMCTwgnC6ttbWMxQNtfdNnPMfevXU3esfMS4PFkVvDNDX6",
        "public_key": "STM7wWqTddXHr4uDJqbFBA4dEa2R2A7GoEPzrCakEdWAKrULuF1Jq",
        "account_name": "account-61",
    },
    {
        "private_key": "5KUrWes8EExsrSJRufLeA2mMPQdjCGS8LfHZgiMsk8BTKxQ8Rww",
        "public_key": "STM4xUWVu5ecKuhB23u3HQqaBP4xXGsGLUjiTY1nSBQgkTq4iw1W8",
        "account_name": "account-62",
    },
    {
        "private_key": "5KQV54oEW95uhSTwF7vzz6mwWUL87rbbYHLUz4xUUAHh12ryiQY",
        "public_key": "STM7k5QaYYCiSMn5A6snexPoaF6T5FWEiGsrUuSc894jckVcSeYu2",
        "account_name": "account-63",
    },
    {
        "private_key": "5JfNQME8n6gNBzEjvEvfZxygQitaD1eaNWYk4KDGF3UoCq2dXu6",
        "public_key": "STM863HJ8kpFwpVasbFw31stuZbDZdzNhscuVMBMsz1BtLZcnD6HS",
        "account_name": "account-64",
    },
    {
        "private_key": "5KifS1mxscoi9iGEFb5cKTxE31z9wLPdM3z5LXdUDtmLt5AhTUd",
        "public_key": "STM7w9Ss8hSXzwatMMJ7aWPhCFT6cTfB4Qy7XvBBEsxGrtoVb6dDJ",
        "account_name": "account-65",
    },
    {
        "private_key": "5JSoYku5fVCi2vhvDbx5UD3ZPd4dUzfDbXVQtk6tAguA6195VFY",
        "public_key": "STM6q9UBxqk5k8RKbCtT6r4ztFTy9TWJ7ULuuCcJRprEG4pWLrK7f",
        "account_name": "account-66",
    },
    {
        "private_key": "5JbwbvrTnPsUKgDHK5DTuvKbzyYMwe7JpbD4v6XkRqp6MJXKiKY",
        "public_key": "STM5YwVLiDMEmJgnBxLU1sTjTL3TcQ41hetkZ6SBjyNUvQWj892Le",
        "account_name": "account-67",
    },
    {
        "private_key": "5KMDG5xm3oBAoHKYED8xvfNmyfdZ9WBQTfwSoKRP22YZUBtTNu5",
        "public_key": "STM87dsYnEsazgxjrWJ6y4ado6DGuHtykRyAfv3gu7EpXqmupAuRp",
        "account_name": "account-68",
    },
    {
        "private_key": "5JXaTpqJSudXV1ZZKpEwShqM4YYXmTX3BwmPZpNGkQzMpJAQCQT",
        "public_key": "STM8HB5Q5mHHgopUDFvWKJuYeXCs9kMzo5t3ddgHRmYUwejTYPzwd",
        "account_name": "account-69",
    },
    {
        "private_key": "5JqwpnzDwTmrQ8XMVGsN8HHUxJv7kpf24kWTMfXTs14thwjMfhj",
        "public_key": "STM8WULhTuiy7oJr1quDwwAuS1Z84wiawFQ2uvSrzTtD3YU2DiGr5",
        "account_name": "account-70",
    },
    {
        "private_key": "5Hshg6xNyan3e5syHCQsT1R7BtD8SJbT976cz9WrgxTS5tNm1eZ",
        "public_key": "STM7EKSBzHscZNqZtYncscLq3wBdSfJx4uP9a99qiEjUnkuV3zzFH",
        "account_name": "account-71",
    },
    {
        "private_key": "5JBFRE1jYjE6uN9kaqTJfvLUY6at86gyNo4ykWdbqy7naiV7BrS",
        "public_key": "STM5x66CnBrFvAr7Rg1pDVG1oGcDCk3K7PxvPLBU8USVxNQfwW2Zi",
        "account_name": "account-72",
    },
    {
        "private_key": "5HyLDWnBK8aL33MomFy9Wzu5Mi8FMUKuCPddqpARcJDLJuR22Ut",
        "public_key": "STM5c7gX6sZRgS3kUnrJY5Ct22Mu5PLPTbLQZnQbPrtBUiKjn9uPX",
        "account_name": "account-73",
    },
    {
        "private_key": "5K53B2JMrPKdjktW5JiymgjJ8jHVgQ1MCwejRAhPS3MZpqziWCC",
        "public_key": "STM7V5MwB5ndY92wou4eSTJa4eFLSL6X7NTTtWVzuVkS5vfZoZpqg",
        "account_name": "account-74",
    },
    {
        "private_key": "5J3eCcXkvwHdEH7rtZuwqxTteo6zMMKxXPra4Jgjz6sszg8P8o6",
        "public_key": "STM7mikUKCa5o9nc1gxvPnkMhVatpdMzSiNoVjvFLfGtJLVB4fLEz",
        "account_name": "account-75",
    },
    {
        "private_key": "5JAdEMbjadnj7Yn7UXTxLYBQYe2cY1ip3t23PFcdjuiULiDHbbZ",
        "public_key": "STM8F8NY4WtJ1HPT39ysotDXYCUQmFThwDnWkAcdvroim6WdWgxqg",
        "account_name": "account-76",
    },
    {
        "private_key": "5JhY5KXwEUgZYG4iRGM2UZyGMhaQBgzyG3tVh6vS7iVV7vwGddL",
        "public_key": "STM52PPNLR8nFm8fBhWyu17Zi1sNNeLHQiTByUzCWqESUQaXZiJxe",
        "account_name": "account-77",
    },
    {
        "private_key": "5K4YPoRGwRUnv7GtwvLoSW5oPjnY2kpDYMuNcMtYK917NCCPk8Y",
        "public_key": "STM6X6QDQiEnyhmPvtcC7BQcGvWkMVUr1EySrdGFxa4EHVx62yGmA",
        "account_name": "account-78",
    },
    {
        "private_key": "5JYkXTB3uidSAydjU1zjhHURfXD34qHNmmHAbdqJyArmBCibmqZ",
        "public_key": "STM8EHLuDNdGSryuzwzwrTj7yrkZadFd5cdjtksSKEacrzD4N83md",
        "account_name": "account-79",
    },
    {
        "private_key": "5HrZtDR3CW3UKayyWWvPz9EFwjMW9V1d8X3W1YYZzMRq1JrmGPB",
        "public_key": "STM54yP4FQ6jHNjVhFaxg7Vjdc4XK7UTh4XoAi6kAGr2LTiojGWgD",
        "account_name": "account-80",
    },
    {
        "private_key": "5JmiGhw9AKwouwDot4EefgXUjPd9EAecDcMeFmZxykqpKiBFpN3",
        "public_key": "STM84tkM8HevcGu8RedV9i9NCYPYvizjqHgDPRsQP2NfamJrepim2",
        "account_name": "account-81",
    },
    {
        "private_key": "5JXxbUk4sjYfk1E7PCYiPmnzVyW1SCisr1tPNpYwVutaMvTgsmY",
        "public_key": "STM7APKM2ZAZH55JJFQPrxgq1RfYdru7Gx7qj1DFVvkdk1nGecB6v",
        "account_name": "account-82",
    },
    {
        "private_key": "5JDZREighZFzXmc7zvqE8az2s5jJT24Fsqd3W1eHuFukpjZfbt6",
        "public_key": "STM8i2BwoxMRqorUpfEpkykpPrgdBywGfed4qGrDXDqX1YHzRERem",
        "account_name": "account-83",
    },
    {
        "private_key": "5J66DexQGjpbVfCGiQEScmzEfaXvdwLRcm7nib33jGZ8vz5Vtzz",
        "public_key": "STM8bhH7XKH61AMM7LzsmMuTifBw52FWTxBvmigqydV74neNwxjKa",
        "account_name": "account-84",
    },
    {
        "private_key": "5KDBn4zexoUyVjP2JhZzgxQwcCiedCi8Y4SNnfcgr1pDicBhaZx",
        "public_key": "STM5aH1DieLRUBVhCEqdMFqLzA3B6EEKJbXQJSkrvXkHS4RyucoUb",
        "account_name": "account-85",
    },
    {
        "private_key": "5KAaeyLGqEqDbtzKwavA5k8vVxA6FWgvZWUHjeixfn3n6Fwk5PL",
        "public_key": "STM8DLgnTvaenmfMwZwRa8D8jp945tEYMcca3HBM2R3rZmrxpnwH2",
        "account_name": "account-86",
    },
    {
        "private_key": "5Jwqd3C3L41tU98qmUaXxhQufx6fBhxaQzwx87dKENrLH9rBzUJ",
        "public_key": "STM8D23ifq29k9J6TLg7cp8Ph8EDrnove7UeKM2L7nSAz1JZawSMJ",
        "account_name": "account-87",
    },
    {
        "private_key": "5JdkqcYRmrsgZbx4QdFS7jedXBcUuzgKmYrkwwc7EjScVDfcBsm",
        "public_key": "STM6Xb3iv5oPbsWyN7ZkqBm3htmPWGiVimLML4ngWqAaXMhBQu7gk",
        "account_name": "account-88",
    },
    {
        "private_key": "5JwoTu5AwPwtSARdxzjqb7ufSLSFYn1ebTGnrXc3BrEa4jk23Qn",
        "public_key": "STM7caqZxY38tB9wYM4ewyxAV8xmhmydbkrPYwmeibpwEoCZZDTkt",
        "account_name": "account-89",
    },
    {
        "private_key": "5J2EyKZYWQ1NKNXsdgK1XBC6prJdHNJTLYFEmUEHN255PACCZq5",
        "public_key": "STM8PgWRwSY9rFrWMd9Qn7Qim5t3kk2mfi3ZuUTt2fnMkiw3r7HSw",
        "account_name": "account-90",
    },
    {
        "private_key": "5JoErPsvdFyZiXth4XWvBdTrTxoVccB754FbQF2hfjauwjC2Rsv",
        "public_key": "STM6EkYBjHZZUghd5JP53eRyeGWo4TdyENie2CoSZRuq5h4qjYFB1",
        "account_name": "account-91",
    },
    {
        "private_key": "5JjRzYBgVSTp2pW9ebPf9Ce4zN8wLM3VWgGFe4izLBZUDD7acfq",
        "public_key": "STM8YQPKPNiuriErJBSSUnPc7FrfvgG3Q7udhbWUWaTp2YAZFe8xD",
        "account_name": "account-92",
    },
    {
        "private_key": "5J9EjfRWTcdFKzLf4J7ovpMLU8QDRxwXdSGuaNqSsrN1d2znov7",
        "public_key": "STM68N9LCQyT946AEV3Ci5pGjodwPNy1sg2HQh7b8FDMvH1ZYdYSk",
        "account_name": "account-93",
    },
    {
        "private_key": "5J7eTQmuabtAz6FRn4BkSDmEpUBhtUhZEMWaLniF4Lkq9TMwBSV",
        "public_key": "STM8ZeExfiuBMqEwEEFVnV4vuJPUJeGquDQNhXcWtBzxFQwpuW4i5",
        "account_name": "account-94",
    },
    {
        "private_key": "5HwVtrkSfDWPnS9PLDBBJ1SkzSJkkrkaVHhaUP4n8BxSs6k58pM",
        "public_key": "STM88v1WXpengpUep796EFMEjYbsQVazimn3D73qifTt7S81EcAjj",
        "account_name": "account-95",
    },
    {
        "private_key": "5HuNf2imXAstuUCsaNzbHcTwbUQzsFXM4GZbXLYKR5PqU9hC8e7",
        "public_key": "STM6E4JYxdx8kEYTa31U254YbGbv7yEGVBBZ2dygonJZmbEzDe4tZ",
        "account_name": "account-96",
    },
    {
        "private_key": "5J4SkervuYB9zcKXrbFiKsigH5P7wy8tUsYL9sTfGwh1F6fbfL2",
        "public_key": "STM7Y9qpTEyX2giAjk2ig87VWNJzUkFz55XSvYYLM6rijqrUy7qG8",
        "account_name": "account-97",
    },
    {
        "private_key": "5K26jLJ9cUgAHMJtFhZwMJjrXscBgAqwc3c5UDxHxAAjWTg2Ph1",
        "public_key": "STM6E1323tK5tULYW6EypotKxKqRPCsQpGwEBS3NkziKDZ8LTgnBS",
        "account_name": "account-98",
    },
    {
        "private_key": "5KQ9RV6YZzrUL7DX7vkBn46zvE7SNiG7YMZxhWZyp6H9PmiWv5H",
        "public_key": "STM5WYudvEvaozVNVPXvWAYdVtkvyjRG1U9Rd3aeSS4ZzxoQ663ta",
        "account_name": "account-99",
    },
    {
        "private_key": "5KeTAa6TCFkEcmn1EmBAMakPgUNWPgeV1WiSfTM8oTCyR4sY5Qm",
        "public_key": "STM7ykffXM9oE1FyBpVhRaCfBpfyJnoafF81ZP5vaGEyDCmXF3mGq",
        "account_name": "account-100",
    },
]

MAX_ACCOUNT_DATA_RANGE: Final[int] = 100


class AccountCredentials(KeyPair):
    name: str

    @classmethod
    def create(cls, account_index: int | None = None) -> AccountCredentials:
        if account_index is None:
            account_index = random.randint(0, MAX_ACCOUNT_DATA_RANGE - 1)  # noqa: S311

        account_data = ACCOUNTS_DATA[account_index]
        return AccountCredentials(
            name=account_data.get("account_name"),
            public_key=account_data.get("public_key"),
            private_key=account_data.get("private_key"),
        )

    @classmethod
    def create_multiple(cls, number_of_accounts: int) -> list[AccountCredentials]:
        account_indexes = random.sample(range(MAX_ACCOUNT_DATA_RANGE), number_of_accounts)
        return [AccountCredentials.create(account_index) for account_index in account_indexes]
