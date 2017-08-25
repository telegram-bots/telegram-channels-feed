package com.github.telegram_bots.channels_feed

import mu.KLogging
import org.springframework.boot.ApplicationArguments
import org.springframework.boot.ApplicationRunner
import org.springframework.boot.SpringApplication
import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.cache.annotation.EnableCaching
import org.springframework.core.env.Environment

@SpringBootApplication
@EnableCaching
class ProcessorApplication(private val env: Environment) : ApplicationRunner {
    override fun run(args: ApplicationArguments) {
        logger.info { env }
    }

    companion object : KLogging() {
        @JvmStatic
        fun main(args: Array<String>) {
            SpringApplication.run(ProcessorApplication::class.java, *args)
        }
    }
}
